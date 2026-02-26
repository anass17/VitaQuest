import mlflow


def setup_mlflow(name):
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment(name)


def start_run(name):
    return mlflow.start_run(run_name=name)


def log_params(params: dict):
    mlflow.log_params(params)


def log_metrics(metrics: dict):
    mlflow.log_metrics(metrics)


def log_text(text: str, file_name: str):
    mlflow.log_text(text, file_name)


def log_dict(data: dict, file_name: str):
    mlflow.log_dict(data, file_name)