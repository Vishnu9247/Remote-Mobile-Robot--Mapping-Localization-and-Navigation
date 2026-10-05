"""Local learning API: HTTP queues work, ROS callbacks own the action client."""
import json
import queue
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus
from .goals import validate_goal, make_goal


class MissionAPI(Node):
    def __init__(self):
        super().__init__('mission_api')
        self.client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        self.jobs = queue.Queue()
        self.lock = threading.Lock()
        self.state = {'status': 'IDLE', 'detail': ''}
        self.goal_handle = None
        self.cancel_requested = False
        self.create_timer(0.05, self.process_jobs)
        self.server = ThreadingHTTPServer(('127.0.0.1', 8000), self.handler_class())
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.get_logger().info('Mission API: http://127.0.0.1:8000 (local machine only)')

    def set_state(self, status, detail=''):
        with self.lock:
            self.state = {'status': status, 'detail': detail}

    def handler_class(self):
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def setup(self):
                super().setup()
                self.connection.settimeout(5.0)

            def respond(self, code, data):
                body = json.dumps(data).encode()
                self.send_response(code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.path != '/robot/status':
                    self.respond(404, {'error': 'Unknown endpoint'})
                    return
                with owner.lock:
                    state = dict(owner.state)
                self.respond(200, state)

            def do_POST(self):
                if self.path == '/robot/cancel':
                    owner.jobs.put(('cancel', None))
                    self.respond(202, {'status': 'Cancellation queued'})
                    return
                if self.path != '/robot/move':
                    self.respond(404, {'error': 'Unknown endpoint'})
                    return
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                    if not 0 < length <= 1024:
                        raise ValueError('Body must be between 1 and 1024 bytes')
                    values = validate_goal(json.loads(self.rfile.read(length)))
                except (ValueError, UnicodeError, TimeoutError) as error:
                    self.respond(400, {'error': str(error)})
                    return
                with owner.lock:
                    if owner.state['status'] in ('QUEUED', 'SENDING', 'RUNNING', 'CANCELING'):
                        busy = True
                    else:
                        busy = False
                        owner.state = {'status': 'QUEUED', 'detail': ''}
                        owner.jobs.put(('move', values))
                self.respond(409 if busy else 202, {'status': 'Busy' if busy else 'QUEUED'})

            def log_message(self, format, *args):
                pass

        return Handler

    def process_jobs(self):
        while not self.jobs.empty():
            kind, values = self.jobs.get_nowait()
            if kind == 'cancel':
                self.cancel_requested = True
                if self.goal_handle is not None:
                    self.set_state('CANCELING')
                    self.goal_handle.cancel_goal_async()
                continue
            self.cancel_requested = False
            if not self.client.server_is_ready():
                self.set_state('FAILED', 'Nav2 action server unavailable')
                continue
            self.set_state('SENDING')
            future = self.client.send_goal_async(make_goal(*values, self.get_clock().now().to_msg()))
            future.add_done_callback(self.accepted)

    def accepted(self, future):
        try:
            handle = future.result()
            if not handle.accepted:
                self.set_state('REJECTED', 'Nav2 rejected the goal')
                return
            self.goal_handle = handle
            self.set_state('RUNNING')
            handle.get_result_async().add_done_callback(self.finished)
            if self.cancel_requested:
                self.set_state('CANCELING')
                handle.cancel_goal_async()
        except Exception as error:
            self.set_state('FAILED', str(error))

    def finished(self, future):
        self.goal_handle = None
        try:
            result = future.result()
            statuses = {GoalStatus.STATUS_SUCCEEDED: 'SUCCEEDED', GoalStatus.STATUS_CANCELED: 'CANCELED',
                        GoalStatus.STATUS_ABORTED: 'FAILED'}
            self.set_state(statuses.get(result.status, 'FAILED'), f'Nav2 status {result.status}')
        except Exception as error:
            self.set_state('FAILED', str(error))


def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = MissionAPI()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.goal_handle is not None and rclpy.ok():
            future = node.goal_handle.cancel_goal_async()
            rclpy.spin_until_future_complete(node, future, timeout_sec=2.0)
        node.server.shutdown()
        node.server.server_close()
        node.thread.join(timeout=2.0)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
