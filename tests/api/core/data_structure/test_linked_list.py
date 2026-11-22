from typing import cast
from uuid import UUID, uuid4

import pytest
from pytest_mock import MockerFixture

from src.core import LinkedList, LinkedNode
from src.core.data_structure.linked_list import AddLinkedNodeMode, GetLinkedListMode


def make_linked_list(*items: str) -> LinkedList:
    return LinkedList.create_from_ordered_list(ordered_list=list(items))


class TestLinkedNode:
    def test_default_id_and_next(self):
        node = LinkedNode(item="first")
        assert isinstance(node.id, UUID)
        assert node.next is None

    def test_explicit_id_and_next(self):
        node_id, next_id = uuid4(), uuid4()

        node = LinkedNode(id=node_id, next=next_id, item="first")
        assert node.id == node_id
        assert node.next == next_id

    def test_string_representation(self):
        node = LinkedNode(item=42)

        result = str(node)
        assert result == "42"


class TestLinkedList:
    def test_empty_state(self):
        linked_list = LinkedList()
        assert linked_list.linked_list == {}
        assert linked_list.first_node is None
        assert linked_list.last_node is None
        assert linked_list.node_count == 0

    def test_counts_nodes(self):
        linked_list = make_linked_list("first", "second")

        count = linked_list.node_count
        assert count == 2

    def test_string_representation_of_empty_list(self):
        linked_list = LinkedList()

        result = str(linked_list)
        assert result == "Length: 0 | Items: "

    def test_string_representation_in_traversal_order(self):
        linked_list = make_linked_list("first", "second")
        linked_list.reverse()

        result = str(linked_list)
        assert result == "Length: 2 | Items: second -> first"


class TestCreateFromOrderedList:
    def test_empty_list(self):
        linked_list = LinkedList.create_from_ordered_list(ordered_list=[])
        assert linked_list.get_ordered_list() == []
        assert linked_list.first_node is None
        assert linked_list.last_node is None

    def test_single_item(self):
        linked_list = LinkedList.create_from_ordered_list(ordered_list=["first"])

        (node,) = linked_list.get_ordered_list()
        assert node.item == "first"
        assert linked_list.first_node == linked_list.last_node == node.id

    def test_multiple_items_preserve_order(self):
        items = ["first", "second", "third"]

        linked_list = LinkedList.create_from_ordered_list(ordered_list=items)
        assert [node.item for node in linked_list.get_ordered_list()] == items


class TestAddLinkedNode:
    def test_first_node_sets_both_endpoints(self):
        linked_list = LinkedList()
        node = LinkedNode(item="first")

        linked_list.add_node(node)
        assert linked_list.first_node == linked_list.last_node == node.id
        assert linked_list.linked_list == {node.id: node}

    @pytest.mark.parametrize("mode", ["default", "append"])
    def test_links_to_existing_tail(self, mode: AddLinkedNodeMode):
        first = LinkedNode(item="first")
        second = LinkedNode(item="second")
        linked_list = LinkedList()
        linked_list.add_node(first)

        linked_list.add_node(second, mode=mode)
        assert first.next == second.id
        assert linked_list.first_node == first.id
        assert linked_list.last_node == second.id

    def test_no_tail_preserves_existing_head(self):
        linked_list = make_linked_list("first")
        head_id = linked_list.first_node
        linked_list.last_node = None
        node = LinkedNode(item="second")

        linked_list.add_node(node)
        assert linked_list.first_node == head_id
        assert linked_list.last_node == node.id

    def test_unsupported_mode_leaves_list_unchanged(self):
        linked_list = make_linked_list("first")
        before = linked_list.model_copy(deep=True)
        node = LinkedNode(item="second")

        linked_list.add_node(node, mode=cast(AddLinkedNodeMode, "unsupported"))
        assert linked_list == before


class TestGetNextLinkedNode:
    def test_returns_first_node_without_argument(self):
        linked_list = make_linked_list("first", "second")

        node = linked_list.get_next_node()
        assert node is not None
        assert node.item == "first"

    def test_returns_successor(self):
        linked_list = make_linked_list("first", "second")
        first = linked_list.get_next_node()

        next_node = linked_list.get_next_node(first)
        assert next_node is not None
        assert next_node.item == "second"

    def test_returns_none_at_tail(self):
        linked_list = make_linked_list("first")
        (tail,) = linked_list.get_ordered_list()

        result = linked_list.get_next_node(tail)
        assert result is None

    def test_no_first_node(self):
        linked_list = LinkedList()

        with pytest.raises(ValueError, match="no first node assigned"):
            linked_list.get_next_node()

    def test_missing_first_node_reference(self):
        missing_id = uuid4()
        linked_list = LinkedList(first_node=missing_id)

        with pytest.raises(KeyError, match=str(missing_id)):
            linked_list.get_next_node()


class TestGetOrderedLinkedList:
    def test_empty_list(self):
        linked_list = LinkedList()

        nodes = linked_list.get_ordered_list()
        assert nodes == []

    def test_single_node(self):
        linked_list = make_linked_list("first")

        nodes = linked_list.get_ordered_list()
        assert [node.item for node in nodes] == ["first"]

    @pytest.mark.parametrize("mode", ["default", "ordered"])
    def test_preserves_traversal_order(self, mode: GetLinkedListMode):
        linked_list = make_linked_list("first", "second", "third")
        linked_list.reverse()

        nodes = linked_list.get_ordered_list(mode=mode)
        assert [node.item for node in nodes] == ["third", "second", "first"]

    def test_reversed_mode_preserves_original_links(self):
        linked_list = make_linked_list("first", "second", "third")
        before = linked_list.model_copy(deep=True)

        nodes = linked_list.get_ordered_list(mode="reversed")
        assert [node.item for node in nodes] == ["third", "second", "first"]
        assert linked_list == before

    def test_nonempty_list_without_first_node(self):
        linked_list = make_linked_list("first")
        linked_list.first_node = None

        with pytest.raises(ValueError, match="no first node assigned"):
            linked_list.get_ordered_list()

    def test_cycle_detection(self, mocker: MockerFixture):
        linked_list = make_linked_list("first")
        (node,) = linked_list.get_ordered_list()
        node.next = node.id
        get_next_node = linked_list.get_next_node
        traversals = iter(range(3))

        def bounded_get_next_node(node: LinkedNode | None = None) -> LinkedNode | None:
            next(traversals)
            return get_next_node(node)

        mocker.patch.object(
            LinkedList, "get_next_node", side_effect=bounded_get_next_node
        )

        with pytest.raises(ValueError, match="Potential infinite looping detected"):
            linked_list.get_ordered_list()


class TestReverseLinkedList:
    def test_empty_list(self):
        linked_list = LinkedList()

        linked_list.reverse()
        assert linked_list == LinkedList()

    def test_single_node(self):
        linked_list = make_linked_list("first")
        before = linked_list.model_copy(deep=True)

        linked_list.reverse()
        assert linked_list == before

    def test_multiple_nodes_rewire_links_and_swap_endpoints(self):
        linked_list = make_linked_list("first", "second", "third")
        first, second, third = linked_list.get_ordered_list()

        linked_list.reverse()
        assert linked_list.first_node == third.id
        assert linked_list.last_node == first.id
        assert (third.next, second.next, first.next) == (second.id, first.id, None)

    def test_reversing_twice_restores_original_order(self):
        linked_list = make_linked_list("first", "second", "third")
        before = linked_list.model_copy(deep=True)

        linked_list.reverse()
        linked_list.reverse()
        assert linked_list == before


class TestModifyAllLinkedNodeItems:
    def test_empty_list_does_not_call_modifier(self):
        linked_list = LinkedList()

        def modifier(node: LinkedNode) -> LinkedNode:
            pytest.fail("The modifier should not run for an empty list")

        linked_list.modify_all_node_items(mod_func=modifier)
        assert linked_list.node_count == 0

    def test_replaces_every_node_and_preserves_traversal_order(self):
        linked_list = make_linked_list("first", "second")
        original = linked_list.get_ordered_list()

        def modifier(node: LinkedNode) -> LinkedNode:
            return node.model_copy(update={"item": node.item.upper()})

        linked_list.modify_all_node_items(mod_func=modifier)

        nodes = linked_list.get_ordered_list()
        assert [node.item for node in nodes] == ["FIRST", "SECOND"]
        assert [node.id for node in nodes] == [node.id for node in original]
        assert [node.item for node in original] == ["first", "second"]

    def test_modifier_failure_propagates(self):
        linked_list = make_linked_list("first")
        before = linked_list.model_copy(deep=True)

        def modifier(node: LinkedNode) -> LinkedNode:
            raise RuntimeError("Modifier failed")

        with pytest.raises(RuntimeError, match="Modifier failed"):
            linked_list.modify_all_node_items(mod_func=modifier)

        assert linked_list == before
