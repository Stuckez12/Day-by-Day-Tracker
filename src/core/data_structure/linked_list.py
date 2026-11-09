import logging
from typing import Any, Callable, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


AddLinkedNodeMode = Literal["default", "append"]
GetLinkedListMode = Literal["default", "ordered", "reversed"]

ERR_NO_FIRST_NODE_FOUND = ValueError("Corrupted LinkedList has no first node assigned")


class LinkedNode(BaseModel):
    id: UUID = Field(default_factory=lambda: uuid4())
    next: UUID | None = Field(default=None)

    item: Any

    def __str__(self) -> str:
        return str(self.item)


class LinkedList(BaseModel):
    linked_list: dict[UUID, LinkedNode] = Field(default_factory=dict)

    first_node: UUID | None = Field(default=None)
    last_node: UUID | None = Field(default=None)

    def __str__(self) -> str:
        logging.info("Getting")
        ordered_items = self.get_ordered_list()
        logging.info("Formatting")
        traversal_str = " -> ".join(str(item) for item in ordered_items)
        logging.info("Returning")

        return f"Length: {self.node_count} | Items: {traversal_str}"

    @property
    def node_count(self) -> int:
        return len(self.linked_list)

    @classmethod
    def create_from_ordered_list(cls, *, ordered_list: list[Any]) -> Self:
        linked_list = cls()

        for item in ordered_list:
            node = LinkedNode(item=item)

            linked_list.add_node(node)

        return linked_list

    def add_node(
        self,
        linked_node: LinkedNode,
        mode: AddLinkedNodeMode = "default",
    ):
        match mode:
            case "default" | "append":
                self.linked_list[linked_node.id] = linked_node

                last_node_id = self.last_node
                self.last_node = linked_node.id

                if last_node_id is None:
                    if self.first_node is None:
                        # Set only when both first and last node were none.
                        # This assumes that there are no nodes in the list.
                        self.first_node = self.last_node

                    return self

                self.linked_list[last_node_id].next = linked_node.id

        return self

    def get_next_node(self, node: LinkedNode | None = None) -> LinkedNode | None:
        if node is None:
            if self.first_node is None:
                raise ERR_NO_FIRST_NODE_FOUND

            return self.linked_list[self.first_node]

        if node.next is None:
            return None

        return self.linked_list[node.next]

    def get_ordered_list(self, mode: GetLinkedListMode = "default") -> list[LinkedNode]:
        if len(self.linked_list) == 0:
            return []

        if self.first_node is None:
            raise ERR_NO_FIRST_NODE_FOUND

        linked_list = []
        node = self.get_next_node()

        nodes_searched = 1

        while node is not None:
            linked_list.append(node)
            node = self.get_next_node(node)

            if nodes_searched > self.node_count:
                raise ValueError(
                    "Potential infinite looping detected. More nodes were retrieved than present in linked list"
                )

        if mode == "reversed":
            linked_list.reverse()

        return linked_list

    def modify_all_node_items(
        self, *, mod_func: Callable[[LinkedNode], LinkedNode]
    ) -> None:
        for node_id, node in self.linked_list.items():
            self.linked_list[node_id] = mod_func(node)
