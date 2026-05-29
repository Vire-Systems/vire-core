import argparse, json
import utils.state as state

def load_parser():
    parser = argparse.ArgumentParser(description = "An isolated,individual worker process handling builds.")

    parser.add_argument(
        '--json_struct',
        type = str,
        required = True,
        help = """JSON structure containing state. Example: '{"job_uuid":"<job_uuid>", "remote":"https://github.com/user/repo_name", "user_uuid":"<user_uuid>", "framework":"<framework>","pm":"<package manager>."install_req":"<Bool>","repo_name":"<name>"}'""")
    args = parser.parse_args()
    json_struct: dict = json.loads(args.json_struct)

    # Variables updation.
    state.job_uuid = json_struct.get("job_uuid")
    state.remote = json_struct.get("remote")
    state.install_req = json_struct.get("install_req")
    state.framework = json_struct.get("framework")
    state.package_manager = json_struct.get("pm")
    state.repo_name = json_struct.get("repo_name")
    #TODO: Update the other ones when needed.