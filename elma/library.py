class Library:
    uuids = (type("UUIDs", (object,), {}))()
    process_headers = (type("UUIDs", (object,), {}))()

    def register_uuid(self, name: str, uuid: str):
        setattr(self.uuids, name, uuid)

    def register_process(self, name: str, header: int):
        setattr(self.process_headers, name, header)


library = Library()
library.register_uuid("Contractor", "1fb7545c-b103-44b1-9b01-dacb986db75d")
library.register_uuid("ContractorLegal", "3325eab1-fe46-4900-a617-c6fb54ac24c0")
library.register_uuid("NaryadZakaz", "cc53a918-3136-46ba-b938-d17289eb2ce4")
library.register_uuid("SLA", "2fd01a0d-0784-44e2-bd8c-231acb60e049")
library.register_uuid("UgF", "39e7bdac-7ab8-432d-8043-fc505a9e96af")
library.register_uuid("UgK", "85a04379-5e44-403e-aa13-06980cba2ac2")
library.register_process("System02A", 177)
library.register_process("System02B", 178)
