from hw2 import play, init

def test():
    player_A, player_B = init(6, 3)
    assert player_A == [3, 3, 3, 3, 3, 3, 0]
    assert player_B == [3, 3, 3, 3, 3, 3, 0]
    
    assert play(player_A, player_B, 3) == 3
    assert player_A == [3, 3, 3, 0, 4, 4, 1]
    assert player_B == [3, 3, 3, 3, 3, 3, 0]
    
    assert play(player_A, player_B, 0) == 2
    assert player_A == [0, 4, 4, 0, 4, 4, 5]
    assert player_B == [3, 3, 0, 3, 3, 3, 0]
    
    assert play(player_B, player_A, 3) == 3
    assert player_A == [0, 4, 4, 0, 4, 4, 5]
    assert player_B == [3, 3, 0, 0, 4, 4, 1]
    
    assert play(player_B, player_A, 0) == 2
    assert player_A == [0, 4, 0, 0, 4, 4, 5]
    assert player_B == [0, 4, 1, 0, 4, 4, 6]
    
    assert play(player_A, player_B, 4) == 2
    assert player_A == [0, 4, 0, 0, 0, 5, 6]
    assert player_B == [1, 5, 1, 0, 4, 4, 6]
    
    assert play(player_B, player_A, 2) == 2
    assert player_A == [0, 4, 0, 0, 0, 5, 6]
    assert player_B == [1, 5, 0, 1, 4, 4, 6]
    
    assert play(player_A, player_B, 1) == 2
    assert player_A == [0, 0, 1, 1, 1, 6, 6]
    assert player_B == [1, 5, 0, 1, 4, 4, 6]
    
    assert play(player_B, player_A, 1) == 3
    assert player_A == [0, 0, 1, 1, 1, 6, 6]
    assert player_B == [1, 0, 1, 2, 5, 5, 7]
    
    assert play(player_B, player_A, 0) == 2
    assert player_A == [0, 0, 1, 1, 0, 6, 6]
    assert player_B == [0, 0, 1, 2, 5, 5, 9]
    
    assert play(player_A, player_B, 2) == 2
    assert player_A == [0, 0, 0, 2, 0, 6, 6]
    assert player_B == [0, 0, 1, 2, 5, 5, 9]
    
    assert play(player_B, player_A, 3) == 2
    assert player_A == [0, 0, 0, 2, 0, 6, 6]
    assert player_B == [0, 0, 1, 0, 6, 6, 9]
    
    assert play(player_A, player_B, 3) == 2
    assert player_A == [0, 0, 0, 0, 1, 7, 6]
    assert player_B == [0, 0, 1, 0, 6, 6, 9]
    
    assert play(player_B, player_A, 2) == 2
    assert player_A == [0, 0, 0, 0, 1, 7, 6]
    assert player_B == [0, 0, 0, 1, 6, 6, 9]
    
    assert play(player_A, player_B, 4) == 2
    assert player_A == [0, 0, 0, 0, 0, 8, 6]
    assert player_B == [0, 0, 0, 1, 6, 6, 9]
    
    assert play(player_B, player_A, 3) == 2
    assert player_A == [0, 0, 0, 0, 0, 8, 6]
    assert player_B == [0, 0, 0, 0, 7, 6, 9]
    
    assert play(player_A, player_B, 5) == 2
    assert player_A == [0, 0, 0, 0, 0, 0, 15]
    assert player_B == [1, 1, 1, 1, 8, 0, 9]
    
    assert play(player_B, player_A, 3) == 2 #tady je chyba v hw2, vítěznému hráči se musí procnout tah (random_choice)
    assert player_A == [0, 0, 0, 0, 0, 0, 15]
    assert player_B == [1, 1, 1, 0, 9, 0, 9]
    
def main():
    test()
    
if __name__ == "__main__":
    main()