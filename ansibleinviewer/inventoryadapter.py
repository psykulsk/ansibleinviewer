import logging
from typing import List

from ansible.inventory.host import Host
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader

logger = logging.getLogger(__name__)


class InventoryAdapter:
    def __init__(self, inventory_path: str):
        self._inventory = InventoryManager(loader=DataLoader(), sources=inventory_path)

    def _husk_groups(self, hosts, groups, no_groups) -> List[Host]:
        output_hosts = []
        if not no_groups:
            no_groups = []
        if not groups:
            groups = ['all']
        for host in hosts.values():
            if any(g.name in groups for g in host.groups) and \
               not any(ng.name in no_groups for ng in host.groups):
                output_hosts.append(host)
        return output_hosts

    def _husk_variables(self, hosts, variables, no_variables) -> List[Host]:
        output_hosts = []
        if not no_variables:
            no_variables = []
        variable_husked_hosts = []
        if not variables:
            variable_husked_hosts = hosts
        else:
            for host in hosts:
                if any(var in host.get_vars().items() for var in variables) or \
                   any(var[0] in host.get_vars().keys() for var in variables if len(var)<2):
                    variable_husked_hosts.append(host)
        for host in variable_husked_hosts:
            if not any(nvar in host.get_vars().items() for nvar in no_variables) and \
               not any(nvar[0] in host.get_vars().keys() for nvar in no_variables if len(nvar)<2):
                output_hosts.append(host)
        return output_hosts

    def get_hosts(self, groups=None, no_groups=None, variables=None, no_variables=None) -> List[Host]:
        output_hosts = self._husk_groups(self._inventory._inventory.hosts, groups, no_groups)
        output_hosts = self._husk_variables(output_hosts, variables, no_variables)
        return list(output_hosts)
