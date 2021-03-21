from models.load_balancer import LoadBalancer
from factories.base_factory import BaseFactory


class LoadBalancerFactory(BaseFactory):
    def __init__(self):
        super.__init__(self)

    @staticmethod
    def create_new_load_balancer() -> LoadBalancer:
        return LoadBalancer

    @staticmethod
    def delete_load_balancer() -> bool:
        return status_code

    def parse_load_balancer_model(self, load_balancer: LoadBalancer = None) -> dict:
        return {LoadBalancer.__dict__}
