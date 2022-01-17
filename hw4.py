import math
from typing import List, Dict, Tuple, Set

Product = Tuple[str, int, int]


class Package:
    def __init__(self, amount: int, price: int, expiry: str):
        self.amount = amount
        self.price = price
        self.expiry = expiry


class Movement:
    def __init__(self, item: str, amount: int, price: int, tag: str):
        self.item = item
        self.amount = amount
        self.price = price
        self.tag = tag


class Warehouse:
    def __init__(self) -> None:
        self.inventory: Dict[str, List[Package]] = {}
        self.history: List[Movement] = []

    def store(self, item: str, amount: int, price: int, expiry: str,
              tag: str) -> None:
        if item in self.inventory:
            self.inventory[item].append(Package(amount, price, expiry))
            self.sort_by_expiry(item)
        else:
            self.inventory[item] = [Package(amount, price, expiry)]
        self.history.append(Movement(item, amount, price, tag))

    def sort_by_expiry(self, item: str) -> None:
        j = len(self.inventory[item]) - 1
        while j > 0 and \
            self.inventory[item][j].expiry >= \
                self.inventory[item][j-1].expiry:
            self.inventory[item][j],\
                self.inventory[item][j-1] = self.inventory[item][j-1],\
                self.inventory[item][j]
            j -= 1

    def find_inconsistencies(self) -> Set[Product]:
        inconsistencies: List[Product] = []

        if len(self.history) == 0:
            if len(self.inventory) == 0:
                return set()

            for item, package in self.inventory.items():
                if len(package) == 0:
                    continue

                package = sorted(package, key=lambda x: x.price)
                prev_price = package[0].price
                amount = package[0].amount
                for pack in package[1:]:
                    if pack.price != prev_price:
                        inconsistencies.append((item, prev_price, amount))
                        prev_price = pack.price
                        amount = pack.amount
                    else:
                        amount += pack.amount
                inconsistencies.append((item, prev_price, amount))
            return set(inconsistencies)

        hist = self.sum_same_price()
        hist_len = len(hist)

        for itemInv, package in self.inventory.items():
            for pack in package:
                for i in range(hist_len):
                    if hist[i][0] == itemInv and hist[i][1] == pack.price:
                        hist[i] = (hist[i][0], hist[i][1],
                                   hist[i][2] - pack.amount)
                        break
                    if i == hist_len - 1:
                        inconsistencies.append((itemInv, pack.price,
                                                pack.amount))

        inconsistencies.sort()
        length = len(inconsistencies)
        inconsistencies_set: Set[Product] = set()
        if length > 0:
            inconsistencies_set.add((inconsistencies[0][0],
                                    inconsistencies[0][1],
                                    inconsistencies[0][2]))

        i = 1
        while i < length:
            prev_item = inconsistencies[i - 1][0]
            prev_price = inconsistencies[i - 1][1]
            item = inconsistencies[i][0]
            price = inconsistencies[i][1]
            if prev_item == item and price == prev_price:
                amount = inconsistencies[i][2] + inconsistencies[i-1][2]
                inconsistencies_set.remove((prev_item, prev_price,
                                            inconsistencies[i-1][2]))
                inconsistencies_set.add((item, price, amount))
            else:
                inconsistencies_set.add((item, price, inconsistencies[i][2]))
            i += 1

        for item, price, amount in hist:
            if amount != 0:
                inconsistencies_set.add((item, price, -amount))
        return inconsistencies_set

    # sums up elements with same item and price from history into one
    def sum_same_price(self) -> List[Product]:
        hist = self.history[:]
        hist.sort(key=lambda x: (x.item, x.price))
        sumed_up: List[Product] = []
        amount = hist[0].amount
        price = hist[0].price
        item = hist[0].item

        for h in hist[1:]:
            if h.item == item and h.price == price:
                amount += h.amount
            else:
                sumed_up.append((item, price, amount))
                item = h.item
                price = h.price
                amount = h.amount

        sumed_up.append((item, price, amount))
        length = len(sumed_up)
        i = 0

        while i < length:
            if sumed_up[i][2] == 0:
                sumed_up.pop(i)
                length -= 1
            i += 1

        return sumed_up

    def remove_expired(self, today: str) -> List[Package]:
        removed: List[Package] = []
        i = 0
        for item, package in self.inventory.items():
            for pack in package:
                if pack.expiry < today:
                    removed.append(pack)
                    self.history.append(Movement(item,
                                                 -pack.amount,
                                                 pack.price,
                                                 "EXPIRED"))
            for pack in removed[i:]:
                self.inventory[item].remove(pack)
                i = len(removed)
        return removed

    def try_sell(self, item: str, amount: int, price: int,
                 tag: str) -> Tuple[int, int]:
        used_amount = 0
        total_price = 0
        breaker = False
        if item not in self.inventory:
            return (0, 0)
        for pack in self.inventory[item][::-1]:
            if (total_price + pack.price * pack.amount) / \
                    (used_amount + pack.amount) > price:
                if used_amount == 0:
                    return 0, 0
                max_amount = \
                    self.fit_average(pack, total_price / used_amount,
                                     used_amount, price)
                used_amount += max_amount
                total_price += max_amount * pack.price
                send_amount = max_amount
                pack.amount -= max_amount
                breaker = True
            elif amount - pack.amount < 0:
                pack.amount -= amount
                used_amount += amount
                total_price += amount * pack.price
                send_amount = amount
                breaker = True
            else:
                used_amount += pack.amount
                total_price += pack.price * pack.amount
                amount -= pack.amount
                send_amount = pack.amount

            if send_amount > 0:
                self.history.append(Movement(item,
                                             -send_amount,
                                             pack.price, tag))
            if breaker:
                break
            self.inventory[item].pop()
        return used_amount, total_price

    def fit_average(self, pack: Package, prev_avg_price: float,
                    prev_amount: int, price: int) -> int:
        x = prev_amount * (price - prev_avg_price) / (pack.price - price)
        return math.floor(x)

    def average_prices(self) -> Dict[str, float]:
        avg_prices: Dict[str, float] = {}
        for item, inv in self.inventory.items():
            amount = 0
            total_cost = 0
            if len(inv) == 0:
                continue
            for pack in inv:
                amount += pack.amount
                total_cost += pack.price * pack.amount
            avg_prices[item] = total_cost / amount
        return avg_prices

    def best_suppliers(self) -> Set[str]:
        suppliers: Set[str] = set()
        if len(self.history) == 0:
            return suppliers
        hist = self.history.copy()
        move = hist.pop()
        supp_item_amount: List[Tuple[str, str, int]] = [(move.item, move.tag,
                                                         move.amount)]
        while len(hist) > 0:
            move = hist.pop()
            added = False
            for i in range(len(supp_item_amount)):
                if supp_item_amount[i][2] < 1:
                    continue
                if supp_item_amount[i][0] == move.item and\
                        supp_item_amount[i][1] == move.tag:
                    supp_item_amount[i] = (move.item, move.tag, move.amount +
                                           supp_item_amount[i][2])
                    added = True
            if not added:
                supp_item_amount.append((move.item, move.tag, move.amount))

        supp_item_amount.sort()

        max_item, max_tag, max_amount = supp_item_amount[0]
        for item, tag, amount in supp_item_amount[1:]:
            if max_item == item:
                if max_amount < amount:
                    max_tag = tag
                if max_amount == amount:
                    suppliers.add(tag)
            else:
                suppliers.add(max_tag)
                max_item = item
                max_amount = amount
                max_tag = tag
        suppliers.add(max_tag)
        return suppliers


def print_warehouse(warehouse: Warehouse) -> None:
    print("===== INVENTORY =====", end="")
    for item, pkgs in warehouse.inventory.items():
        print(f"\n* Item: {item}")
        print("    amount  price  expiration date")
        print("  ---------------------------------")
        for pkg in pkgs:
            print(f"     {pkg.amount:4d}   {pkg.price:4d}     {pkg.expiry}")
    print("\n===== HISTORY ======")
    print("    item     amount  price   tag")
    print("-------------------------------------------")
    for mov in warehouse.history:
        print(f" {mov.item:^11}   {mov.amount:4d}   "
              f"{mov.price:4d}   {mov.tag}")


def example_warehouse() -> Warehouse:
    wh = Warehouse()

    wh.store("rice", 100, 17, "20220202", "ACME Rice Ltd.")
    wh.store("corn", 70, 15, "20220315", "UniCORN & co.")
    wh.store("rice", 200, 158, "20771023", "RICE Unlimited")
    wh.store("peas", 9774, 1, "20220921", "G. P. a C.")
    wh.store("rice", 90, 14, "20220202", "Theorem's Rice")
    wh.store("peas", 64, 7, "20211101", "Discount Peas")
    wh.store("rice", 42, 9, "20211111", "ACME Rice Ltd.")

    return wh


def test1() -> None:
    wh = example_warehouse()

    for item, length in ('rice', 4), ('peas', 2), ('corn', 1):
        assert item in wh.inventory
        assert len(wh.inventory[item]) == length

    assert len(wh.history) == 7

    # uncomment to visually check the output:
    # print_warehouse(wh)


def test2() -> None:
    wh = example_warehouse()
    assert wh.find_inconsistencies() == set()

    wh.inventory['peas'][0].amount = 9773
    wh.history[4].price = 12

    assert wh.find_inconsistencies() == {
        ('peas', 1, -1),
        ('rice', 14, 90),
        ('rice', 12, -90),
    }


def test3() -> None:
    wh = example_warehouse()
    bad_peas = wh.inventory['peas'][-1]
    assert wh.remove_expired('20211111') == [bad_peas]
    assert len(wh.history) == 8

    mov = wh.history[-1]
    assert mov.item == 'peas'
    assert mov.amount == -64
    assert mov.price == 7
    assert mov.tag == 'EXPIRED'

    assert len(wh.inventory['peas']) == 1


def test4() -> None:
    wh = example_warehouse()
    assert wh.try_sell('rice', 500, 9, 'Pear Shop') == (42, 42 * 9)
    assert len(wh.history) == 8
    assert wh.find_inconsistencies() == set()

    wh = example_warehouse()
    assert wh.try_sell('rice', 500, 12, 'Pear Shop') \
        == (42 + 25, 42 * 9 + 25 * 17)
    assert len(wh.history) == 9
    assert wh.find_inconsistencies() == set()

    wh = example_warehouse()
    assert wh.try_sell('rice', 500, 14, 'Pear Shop') \
        == (42 + 70, 42 * 9 + 70 * 17)
    assert len(wh.history) == 9
    assert wh.find_inconsistencies() == set()

    wh = example_warehouse()
    assert wh.try_sell('rice', 500, 15, 'Pear Shop') \
        == (42 + 100 + 90, 42 * 9 + 100 * 17 + 90 * 14)
    assert len(wh.history) == 10
    assert wh.find_inconsistencies() == set()

    wh = example_warehouse()
    assert wh.try_sell('rice', 500, 16, 'Pear Shop') \
        == (42 + 100 + 90 + 2, 42 * 9 + 100 * 17 + 90 * 14 + 2 * 158)
    assert len(wh.history) == 11
    assert wh.find_inconsistencies() == set()

    # uncomment to visually check the output:
    # print_warehouse(wh)

    wh = example_warehouse()
    assert wh.try_sell('rice', 500, 81, 'Pear Shop') \
        == (42 + 100 + 90 + 200, 42 * 9 + 100 * 17 + 90 * 14 + 200 * 158)
    assert len(wh.history) == 11
    assert wh.find_inconsistencies() == set()


def test5() -> None:
    wh = example_warehouse()

    expected = {
        'rice': 80.875,
        'corn': 15,
        'peas': (9774 + 64 * 7) / (9774 + 64),
    }

    avg_prices = wh.average_prices()

    assert expected.keys() == avg_prices.keys()

    for item in avg_prices:
        assert math.isclose(avg_prices[item], expected[item])

    assert wh.best_suppliers() \
        == {'UniCORN & co.', 'G. P. a C.', 'RICE Unlimited'}


if __name__ == '__main__':
    test1()
    test2()
    test3()
    test4()
    test5()
    wh = Warehouse()
    wh.history = [Movement('rice', 1, 16842753, 'B'), Movement('rice', 257, 2, 'A'),
                    Movement('rice', 2, 67109121, 'A'), Movement('peas', 2, 259, 'BH'),
                    Movement('rice', 1, 5, 'A'), Movement('peas', 16777474, 257, 'EB'),
                    Movement('peas', 6, 258, 'B'), Movement('peas', 646, 10, 'B'),
                    Movement('peas', 16843009, 16843010, 'B'), Movement('peas', 16843778, 17170946, 'B'),
                    Movement('peas', 1, 257, 'B'), Movement('peas', 262, 4, 'B'),
                    Movement('peas', 2, 258, 'BBA'), Movement('peas', 258, 258, 'BBBB'),
                    Movement('corn', 16974082, 259, 'C'), Movement('corn', 257, 2, 'E'),
                    Movement('corn', 40036, 90, 'U'), Movement('hops', 2, 260, 'X'),
                    Movement('hops', 1638913, 246482178, 'd'), Movement('hops', 4261806851, 3508039041, 'e'),
                    Movement('hops', 2, 25017, 'i'), Movement('barley', 235, 127, 'm'),
                    Movement('potatoes', 3484164454, 1400102507, 'm')]
    wh.inventory = {
        'rice': [Package(1, 16842753, '20000201'), Package(257, 2, '20000104'), Package(2, 67109121, '20000102'), Package(1, 5, '19990202')],
        'peas': [Package(2, 259, '22560103'), Package(6, 258, '20000608'), Package(2, 258, '19990602'), Package(262, 4, '19990205'), Package(1, 257, '19990203'), Package(258, 258, '19990202'), Package(16843778, 17170946, '19990202'), Package(16843009, 16843010, '19990102'), Package(646, 10, '19990101'), Package(16777474, 257, '19970201')],
        'corn': [Package(40036, 90, '19990623'), Package(257, 2, '19990401'), Package(16974082, 259, '19990301')],
        'hops': [Package(1638913, 246482178, '19991201'), Package(2, 260, '19990707'), Package(2, 25017, '19981010'), Package(4261806851, 3508039041, '19980512')],
        'barley': [Package(235, 127, '19961031')],
        'potatoes': [Package(3484164454, 1400102507, '19931012')],
    }
    print_warehouse(wh)
    print(wh.try_sell('peas', 50465436, 11352620, 'rB'))