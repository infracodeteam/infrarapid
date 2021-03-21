class BaseFactory(object):
    def export_to_terraform(self) -> str:
        return path_to_terraform_file