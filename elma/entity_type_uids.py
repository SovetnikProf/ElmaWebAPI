class Library:
    def register(self, name: str, uuid: str):
        setattr(self, name, uuid)


library = Library()
library.register("Contractor", "1fb7545c-b103-44b1-9b01-dacb986db75d")
library.register("ContractorLegal", "3325eab1-fe46-4900-a617-c6fb54ac24c0")
library.register("NaryadZakaz", "cc53a918-3136-46ba-b938-d17289eb2ce4")
library.register("SLA", "2fd01a0d-0784-44e2-bd8c-231acb60e049")
library.register("UgF", "39e7bdac-7ab8-432d-8043-fc505a9e96af")
library.register("UgK", "85a04379-5e44-403e-aa13-06980cba2ac2")
