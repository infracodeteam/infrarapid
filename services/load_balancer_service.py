from factories.load_balancer_factory import LoadBalancerFactory
from models.load_balancer import LoadBalancer


class LoadBalancerService(object):
    def __init__(self):
        self.load_balancer_factory = LoadBalancerFactory
        pass

    def create_load_balancer(self) -> LoadBalancer:
        load_balancer_obj = self.load_balancer_factory.create_new_load_balancer()
        return load_balancer_obj

    def get_load_balancer_by_id(self, id: str = None) -> LoadBalancer:
        return LoadBalancer

    def export_load_balancer_to_terraform_file(self, load_balancer: LoadBalancer = None) -> str:
        path_to_file = self.load_balancer_factory.export_to_terraform(load_balancer)
        return path_to_file