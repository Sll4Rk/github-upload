from typing import Dict, List, Optional, Set, Tuple


class Person:
    def __init__(self, pid: int, name: str, birth_year: int,
                 parent: Optional['Person'], children: List['Person']):
        self.pid = pid
        self.name = name
        self.birth_year = birth_year
        self.parent = parent
        self.children = children

    def is_valid(self) -> bool:
        stack: List['Person'] = [self]
        while len(stack) != 0:
            person = stack.pop()
            if person.name == "":
                return False
            if len(person.children) == 0:
                continue
            names: Set[str] = set()
            for child in person.children:
                if child.name in names or\
                   child.birth_year <= person.birth_year:
                    return False
                names.add(child.name)
            stack.extend(person.children)
        return True

    def draw(self, names_only: bool) -> None:
        stack: List[Tuple['Person', int]] = [(self, 0)]
        while len(stack) != 0:
            line = ""
            person, indent = stack.pop()
            dent: Set[int] = set()
            for _, i in stack:
                if i < indent:
                    dent.add(i)
            for i in range(1, indent):
                if i in dent:
                    line = ''.join([line, "│  "])
                else:
                    line = ''.join([line, "   "])
            addToString = person.name
            if not names_only:
                addToString = ''.join([person.name, " (" +
                                       str(person.birth_year) + ')',
                                       " [" + str(person.pid) + ']'])
            if indent == 0:
                line = addToString
            elif len(stack) == 0 or indent != stack[-1][1]:
                line = ''.join([line, "└─ ", addToString])
            else:
                line = ''.join([line, "├─ ", addToString])
            print(line)
            stack.extend(list(map(lambda x: (x, indent + 1),
                                  person.children[::-1])))

    def parents_younger_than(self, age_limit: int) -> Set[int]:
        result: Set[int] = set()
        tpls = self.get_list()
        for person, parent in tpls:
            if not parent:
                continue
            if person.birth_year - parent.birth_year < age_limit:
                result.add(parent.pid)
        return result

    def parents_older_than(self, age_limit: int) -> Set[int]:
        result: Set[int] = set()
        tpls = self.get_list()
        for person, parent in tpls:
            if not parent:
                continue
            if person.birth_year - parent.birth_year > age_limit:
                result.add(parent.pid)
        return result

    def childless(self) -> Set[int]:
        result: Set[int] = set()
        for person, _ in self.get_list():
            if len(person.children) == 0:
                result.add(person.pid)
        return result

    def ancestors(self) -> List['Person']:
        if not self.parent:
            return []
        person: Optional['Person'] = self.parent
        result: List['Person'] = []
        while person:
            result.append(person)
            person = person.parent
        return result[::-1]

    def order_of_succession(self, alive: Set[int]) -> Dict[int, int]:
        children_order = self.sort_children()
        stack: List['Person'] = children_order
        result: Dict[int, int] = {}
        count = 1
        while len(stack) != 0:
            person = stack.pop()
            if person.pid in alive:
                result[person.pid] = count
                count += 1
            children_order = person.sort_children()
            stack.extend(children_order)
        return result

    def remove_extinct_branches(self, alive: Set[int]) -> None:
        people = self.get_list()
        while len(people) != 0:
            person, parent = people.pop()
            if len(person.children) == 0 and person.pid not in alive and\
               parent:
                parent.children.remove(person)

    def get_list(self) -> List[Tuple['Person', Optional['Person']]]:
        person = self
        stack: List[Tuple['Person', Optional['Person']]] = [(person, None)]
        people: List[Tuple['Person', Optional['Person']]] = [(person, None)]
        while len(stack) != 0:
            person, _ = stack.pop()
            for child in person.children:
                people.append((child, person))
                stack.append((child, person))
        return people

    def sort_children(self) -> List['Person']:
        if len(self.children) == 0:
            return []
        result: List['Person'] = [self.children[0]]
        if len(self.children) == 1:
            return result
        for child in self.children[1:]:
            for i in range(len(result)):
                if child.birth_year < result[i].birth_year:
                    result.insert(i, child)
                    break
                if i == len(result) - 1:
                    result.append(child)
        return result[::-1]


def build_family_tree(names: Dict[int, str],
                      children: Dict[int, List[int]],
                      birth_years: Dict[int, int]) -> Optional['Person']:
    pid: Optional[int] = find_start(set(names.keys()), children,
                                    set(birth_years.keys()))
    if pid is None:
        return None
    stack: List[Tuple[int, Optional['Person']]] = [(pid, None)]
    while len(stack) != 0:
        pid, parent = stack.pop()
        if pid not in names or pid not in birth_years:
            return None
        person = Person(pid, names[pid], birth_years[pid], parent, [])
        if not parent:
            head = person
        else:
            parent.children.append(person)
        if pid not in children:
            continue
        children_order = list(map(lambda x: (x, person), children[pid][::-1]))
        stack.extend(children_order)
    return head


def find_start(names_pid_set: Set[int], children: Dict[int, List[int]],
               birth_years_pid: Set[int]) -> Optional[int]:
    if birth_years_pid != names_pid_set:
        return None
    for _, children_list in children.items():
        for child in children_list:
            if child not in names_pid_set:
                return None
            names_pid_set.remove(child)
    if len(names_pid_set) != 1:
        return None
    return names_pid_set.pop()


def valid_family_tree(person: Person) -> bool:
    while person.parent:
        person = person.parent
    return person.is_valid()


def test_one_person() -> None:
    adam = build_family_tree({1: "Adam"}, {}, {1: 1})
    assert isinstance(adam, Person)
    assert adam.pid == 1
    assert adam.birth_year == 1
    assert adam.name == "Adam"
    assert adam.children == []
    assert adam.parent is None

    assert adam.is_valid()
    assert adam.parents_younger_than(18) == set()
    assert adam.parents_older_than(81) == set()
    assert adam.childless() == {1}
    assert adam.ancestors() == []
    assert adam.order_of_succession({1}) == {}


def example_family_tree() -> Person:
    qempa = build_family_tree(
        {
            17: "Qempa'",
            127: "Thok Mak",
            290: "Worf",
            390: "Worf",
            490: "Mogh",
            590: "Kurn",
            611: "Ag'ax",
            561: "K'alaga",
            702: "Samtoq",
            898: "K'Dhan",
            429: "Grehka",
            1000: "Alexander Rozhenko",
            253: "D'Vak",
            106: "Elumen",
            101: "Ga'ga",
        },
        {
            17: [127, 290],
            390: [898, 1000],
            1000: [253],
            127: [611, 561, 702],
            590: [429, 106, 101],
            490: [390, 590],
            290: [490],
            702: [],
        },
        {
            1000: 2366,
            101: 2366,
            106: 2357,
            127: 2281,
            17: 2256,
            253: 2390,
            290: 2290,
            390: 2340,
            429: 2359,
            490: 2310,
            561: 2302,
            590: 2345,
            611: 2317,
            702: 2317,
            898: 2388,
        }
    )

    assert qempa is not None
    return qempa


def test_example() -> None:
    qempa = example_family_tree()
    assert qempa.name == "Qempa'"
    assert qempa.pid == 17
    assert qempa.birth_year == 2256
    assert qempa.parent is None
    assert len(qempa.children) == 2

    thok_mak, worf1 = qempa.children
    assert worf1.name == "Worf"
    assert worf1.pid == 290
    assert worf1.birth_year == 2290
    assert worf1.parent == qempa
    assert len(worf1.children) == 1

    mogh = worf1.children[0]
    assert mogh.name == "Mogh"
    assert mogh.pid == 490
    assert mogh.birth_year == 2310
    assert mogh.parent == worf1
    assert len(mogh.children) == 2

    worf2 = mogh.children[0]
    assert worf2.name == "Worf"
    assert worf2.pid == 390
    assert worf2.birth_year == 2340
    assert worf2.parent == mogh
    assert len(worf2.children) == 2

    alex = worf2.children[1]
    assert alex.name == "Alexander Rozhenko"
    assert alex.pid == 1000
    assert alex.birth_year == 2366
    assert alex.parent == worf2
    assert len(alex.children) == 1

    assert qempa.is_valid()
    assert alex.is_valid()
    assert valid_family_tree(qempa)
    assert valid_family_tree(alex)

    thok_mak.name = ""
    assert not qempa.is_valid()
    assert alex.is_valid()
    assert not valid_family_tree(qempa)
    assert not valid_family_tree(alex)
    thok_mak.name = "Thok Mak"

    thok_mak.birth_year = 2302
    assert not qempa.is_valid()
    assert alex.is_valid()
    assert not valid_family_tree(qempa)
    assert not valid_family_tree(alex)
    thok_mak.birth_year = 2281

    assert qempa.parents_younger_than(12) == set()
    assert qempa.parents_younger_than(15) == {590}
    assert qempa.parents_younger_than(21) == {290, 590}

    assert qempa.parents_older_than(48) == set()
    assert qempa.parents_older_than(40) == {390}

    assert thok_mak.parents_younger_than(21) == set()
    assert thok_mak.parents_older_than(40) == set()

    assert qempa.childless() == {101, 106, 253, 429, 561, 611, 702, 898}
    assert thok_mak.childless() == {611, 561, 702}

    assert alex.ancestors() == [qempa, worf1, mogh, worf2]
    assert thok_mak.ancestors() == [qempa]
    assert qempa.ancestors() == []

    alive = {17, 101, 106, 127, 253, 290, 390, 429,
             490, 561, 590, 611, 702, 898, 1000}
    succession = {
        101: 14,
        106: 12,
        127: 1,
        253: 9,
        290: 5,
        390: 7,
        429: 13,
        490: 6,
        561: 2,
        590: 11,
        611: 3,
        702: 4,
        898: 10,
        1000: 8,
    }

    assert qempa.order_of_succession(alive) == succession

    alive.remove(17)
    assert qempa.order_of_succession(alive) == succession

    alive -= {127, 290, 490, 590}
    assert qempa.order_of_succession(alive) == {
        561: 1,
        611: 2,
        702: 3,
        390: 4,
        1000: 5,
        253: 6,
        898: 7,
        106: 8,
        429: 9,
        101: 10,
    }

    assert mogh.order_of_succession(alive) == {
        390: 1,
        1000: 2,
        253: 3,
        898: 4,
        106: 5,
        429: 6,
        101: 7,
    }


def draw_example() -> None:
    qempa = example_family_tree()
    print("První příklad:")
    qempa.draw(False)

    print("\nDruhý příklad:")
    qempa.children[1].children[0].draw(True)

    alive1 = {101, 106, 253, 429, 561, 611, 702, 898}
    alive2 = {101, 106, 253, 390, 898, 1000}
    for alive in alive1, alive2:
        print(f"\nRodokmen po zavolání remove_extinct_branches({alive})\n"
              "na výchozí osobě:")
        qempa = example_family_tree()
        qempa.remove_extinct_branches(alive)
        qempa.draw(True)

    print(f"\nRodokmen po zavolání remove_extinct_branches({alive})\n"
          "na osobě jménem Mogh:")
    qempa = example_family_tree()
    qempa.children[1].children[0].remove_extinct_branches(alive2)
    qempa.draw(True)


if __name__ == '__main__':
    root = build_family_tree({1: 'Adam', 2: 'Eva', 3: 'Kain'},
                             {1: [2, 3], 2: [3]},
                             {1: 1, 2: 2, 3: 3})
    if root:
        root.draw(False)
    test_one_person()
    test_example()
    # draw_example()  # uncomment to run
