@archive ChooseRandomBattleFolderTextScript
@size 66

/*
 0  1  2  3
 4  5  6  7
 8  9 10 11 12 13
*/

script 0 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Choose the random battle
  folder!
  """
  keyWait
    any = false
  clearMsg

  jump
    target = 1
}

script 1 mmbn6 {
  msgOpen
  textSpeed
    delay = 0

  option // 0
    brackets = 0
    left = 3
    right = 1
    up = 8
    down = 4
  space
    count = 1
  "A"

  option // 1
    brackets = 0
    left = 0
    right = 2
    up = 9
    down = 5
  space
    count = 1
  "B"

  option // 2
    brackets = 0
    left = 1
    right = 3
    up = 10
    down = 6
  space
    count = 1
  "C"

  option // 3
    brackets = 0
    left = 2
    right = 0
    up = 11
    down = 7
  space
    count = 1
  "D\n"

  option // 4
    brackets = 0
    left = 7
    right = 5
    up = 0
    down = 8
  space
    count = 1
  "E"

  option // 5
    brackets = 0
    left = 4
    right = 6
    up = 1
    down = 9
  space
    count = 1
  "F"

  option // 6
    brackets = 0
    left = 5
    right = 7
    up = 2
    down = 10
  space
    count = 1
  "G"

  option // 7
    brackets = 0
    left = 6
    right = 4
    up = 3
    down = 11
  space
    count = 1
  "H\n"

  option // 8
    brackets = 0
    left = 13
    right = 9
    up = 4
    down = 0
  space
    count = 1
  "J"

  option // 9
    brackets = 0
    left = 8
    right = 10
    up = 5
    down = 1
  space
    count = 1
  "K"

  option // 10
    brackets = 0
    left = 9
    right = 11
    up = 6
    down = 2
  space
    count = 1
  "L"

  option // 11
    brackets = 0
    left = 10
    right = 12
    up = 7
    down = 3
  space
    count = 1
  "M"

  option // 12
    brackets = 0
    left = 11
    right = 13
    up = 12
    down = 12
  space
    count = 1
  "Prev"

  option // 13
    brackets = 0
    left = 12
    right = 8
    up = 13
    down = 13
  space
    count = 1
  "Next"

  textSpeed
    delay = 2

  soundDisableChoiceSFX
  select
    default = 0
    BSeparate = true
    disableB = false
    clear = false
    targets = [
      jump = 6,
      jump = 7,
      jump = 8,
      jump = 9,
      jump = 10,
      jump = 11,
      jump = 12,
      jump = 13,
      jump = 14,
      jump = 15,
      jump = 16,
      jump = 17,
      jump = 5,
      jump = 2,
      jump = continue
    ]
  clearMsg
  """
  Cancelled choosing
  random battle folder.
  """
  keyWait
    any = false
  end
}

script 2 mmbn6 {
  msgOpen
  textSpeed
    delay = 0

  option // 0
    brackets = 0
    left = 3
    right = 1
    up = 8
    down = 4
  space
    count = 1
  "N"

  option // 1
    brackets = 0
    left = 0
    right = 2
    up = 9
    down = 5
  space
    count = 1
  "O"

  option // 2
    brackets = 0
    left = 1
    right = 3
    up = 10
    down = 6
  space
    count = 1
  "P"

  option // 3
    brackets = 0
    left = 2
    right = 0
    up = 11
    down = 7
  space
    count = 1
  "Q\n"

  option // 4
    brackets = 0
    left = 7
    right = 5
    up = 0
    down = 8
  space
    count = 1
  "R"

  option // 5
    brackets = 0
    left = 4
    right = 6
    up = 1
    down = 9
  space
    count = 1
  "S"

  option // 6
    brackets = 0
    left = 5
    right = 7
    up = 2
    down = 10
  space
    count = 1
  "T"

  option // 7
    brackets = 0
    left = 6
    right = 4
    up = 3
    down = 11
  space
    count = 1
  "U\n"

  option // 8
    brackets = 0
    left = 13
    right = 9
    up = 4
    down = 0
  space
    count = 1
  "V"

  option // 9
    brackets = 0
    left = 8
    right = 10
    up = 5
    down = 1
  space
    count = 1
  "W"

  option // 10
    brackets = 0
    left = 9
    right = 11
    up = 6
    down = 2
  space
    count = 1
  "X"

  option // 11
    brackets = 0
    left = 10
    right = 12
    up = 7
    down = 3
  space
    count = 1
  "Y"

  option // 12
    brackets = 0
    left = 11
    right = 13
    up = 12
    down = 12
  space
    count = 1
  "Prev"

  option // 13
    brackets = 0
    left = 12
    right = 8
    up = 13
    down = 13
  space
    count = 1
  "Next"

  textSpeed
    delay = 2

  soundDisableChoiceSFX
  select
    default = 0
    BSeparate = true
    disableB = false
    clear = false
    targets = [
      jump = 18,
      jump = 19,
      jump = 20,
      jump = 21,
      jump = 22,
      jump = 23,
      jump = 24,
      jump = 25,
      jump = 26,
      jump = 27,
      jump = 28,
      jump = 29,
      jump = 1,
      jump = 3,
      jump = continue
    ]
  clearMsg
  """
  Cancelled choosing
  random battle folder.
  """
  keyWait
    any = false
  end
}

script 3 mmbn6 {
  msgOpen
  textSpeed
    delay = 0

  option // 0
    brackets = 0
    left = 3
    right = 1
    up = 8
    down = 4
  space
    count = 1
  "Z"

  option // 1
    brackets = 0
    left = 0
    right = 2
    up = 9
    down = 5
  space
    count = 1
  "a"

  option // 2
    brackets = 0
    left = 1
    right = 3
    up = 10
    down = 6
  space
    count = 1
  "b"

  option // 3
    brackets = 0
    left = 2
    right = 0
    up = 11
    down = 7
  space
    count = 1
  "c\n"

  option // 4
    brackets = 0
    left = 7
    right = 5
    up = 0
    down = 8
  space
    count = 1
  "d"

  option // 5
    brackets = 0
    left = 4
    right = 6
    up = 1
    down = 9
  space
    count = 1
  "e"

  option // 6
    brackets = 0
    left = 5
    right = 7
    up = 2
    down = 10
  space
    count = 1
  "f"

  option // 7
    brackets = 0
    left = 6
    right = 4
    up = 3
    down = 11
  space
    count = 1
  "g\n"

  option // 8
    brackets = 0
    left = 13
    right = 9
    up = 4
    down = 0
  space
    count = 1
  "h"

  option // 9
    brackets = 0
    left = 8
    right = 10
    up = 5
    down = 1
  space
    count = 1
  "i"

  option // 10
    brackets = 0
    left = 9
    right = 11
    up = 6
    down = 2
  space
    count = 1
  "j"

  option // 11
    brackets = 0
    left = 10
    right = 12
    up = 7
    down = 3
  space
    count = 1
  "k"

  option // 12
    brackets = 0
    left = 11
    right = 13
    up = 12
    down = 12
  space
    count = 1
  "Prev"

  option // 13
    brackets = 0
    left = 12
    right = 8
    up = 13
    down = 13
  space
    count = 1
  "Next"

  textSpeed
    delay = 2

  soundDisableChoiceSFX
  select
    default = 0
    BSeparate = true
    disableB = false
    clear = false
    targets = [
      jump = 30,
      jump = 31,
      jump = 32,
      jump = 33,
      jump = 34,
      jump = 35,
      jump = 36,
      jump = 37,
      jump = 38,
      jump = 39,
      jump = 40,
      jump = 41,
      jump = 2,
      jump = 4,
      jump = continue
    ]
  clearMsg
  """
  Cancelled choosing
  random battle folder.
  """
  keyWait
    any = false
  end
}

script 4 mmbn6 {
  msgOpen
  textSpeed
    delay = 0

  option // 0
    brackets = 0
    left = 3
    right = 1
    up = 8
    down = 4
  space
    count = 1
  "m"

  option // 1
    brackets = 0
    left = 0
    right = 2
    up = 9
    down = 5
  space
    count = 1
  "n"

  option // 2
    brackets = 0
    left = 1
    right = 3
    up = 10
    down = 6
  space
    count = 1
  "o"

  option // 3
    brackets = 0
    left = 2
    right = 0
    up = 11
    down = 7
  space
    count = 1
  "p\n"

  option // 4
    brackets = 0
    left = 7
    right = 5
    up = 0
    down = 8
  space
    count = 1
  "q"

  option // 5
    brackets = 0
    left = 4
    right = 6
    up = 1
    down = 9
  space
    count = 1
  "r"

  option // 6
    brackets = 0
    left = 5
    right = 7
    up = 2
    down = 10
  space
    count = 1
  "s"

  option // 7
    brackets = 0
    left = 6
    right = 4
    up = 3
    down = 11
  space
    count = 1
  "t\n"

  option // 8
    brackets = 0
    left = 13
    right = 9
    up = 4
    down = 0
  space
    count = 1
  "u"

  option // 9
    brackets = 0
    left = 8
    right = 10
    up = 5
    down = 1
  space
    count = 1
  "v"

  option // 10
    brackets = 0
    left = 9
    right = 11
    up = 6
    down = 2
  space
    count = 1
  "w"

  option // 11
    brackets = 0
    left = 10
    right = 12
    up = 7
    down = 3
  space
    count = 1
  "x"

  option // 12
    brackets = 0
    left = 11
    right = 13
    up = 12
    down = 12
  space
    count = 1
  "Prev"

  option // 13
    brackets = 0
    left = 12
    right = 8
    up = 13
    down = 13
  space
    count = 1
  "Next"

  textSpeed
    delay = 2

  soundDisableChoiceSFX
  select
    default = 0
    BSeparate = true
    disableB = false
    clear = false
    targets = [
      jump = 42,
      jump = 43,
      jump = 44,
      jump = 45,
      jump = 46,
      jump = 47,
      jump = 48,
      jump = 49,
      jump = 50,
      jump = 51,
      jump = 52,
      jump = 53,
      jump = 3,
      jump = 5,
      jump = continue
    ]
  clearMsg
  """
  Cancelled choosing
  random battle folder.
  """
  keyWait
    any = false
  end
}

script 5 mmbn6 {
  msgOpen
  textSpeed
    delay = 0

  option // 0
    brackets = 0
    left = 3
    right = 1
    up = 8
    down = 4
  space
    count = 1
  "y"

  option // 1
    brackets = 0
    left = 0
    right = 2
    up = 9
    down = 5
  space
    count = 1
  "z"

  option // 2
    brackets = 0
    left = 1
    right = 3
    up = 10
    down = 6
  space
    count = 1
  "0"

  option // 3
    brackets = 0
    left = 2
    right = 0
    up = 11
    down = 7
  space
    count = 1
  "1\n"

  option // 4
    brackets = 0
    left = 7
    right = 5
    up = 0
    down = 8
  space
    count = 1
  "2"

  option // 5
    brackets = 0
    left = 4
    right = 6
    up = 1
    down = 9
  space
    count = 1
  "3"

  option // 6
    brackets = 0
    left = 5
    right = 7
    up = 2
    down = 10
  space
    count = 1
  "4"

  option // 7
    brackets = 0
    left = 6
    right = 4
    up = 3
    down = 11
  space
    count = 1
  "5\n"

  option // 8
    brackets = 0
    left = 13
    right = 9
    up = 4
    down = 0
  space
    count = 1
  "6"

  option // 9
    brackets = 0
    left = 8
    right = 10
    up = 5
    down = 1
  space
    count = 1
  "7"

  option // 10
    brackets = 0
    left = 9
    right = 11
    up = 6
    down = 2
  space
    count = 1
  "8"

  option // 11
    brackets = 0
    left = 10
    right = 12
    up = 7
    down = 3
  space
    count = 1
  "9"

  option // 12
    brackets = 0
    left = 11
    right = 13
    up = 12
    down = 12
  space
    count = 1
  "Prev"

  option // 13
    brackets = 0
    left = 12
    right = 8
    up = 13
    down = 13
  space
    count = 1
  "Next"

  textSpeed
    delay = 2

  soundDisableChoiceSFX
  select
    default = 0
    BSeparate = true
    disableB = false
    clear = false
    targets = [
      jump = 54,
      jump = 55,
      jump = 56,
      jump = 57,
      jump = 58,
      jump = 59,
      jump = 60,
      jump = 61,
      jump = 62,
      jump = 63,
      jump = 64,
      jump = 65,
      jump = 4,
      jump = 1,
      jump = continue
    ]
  clearMsg
  """
  Cancelled choosing
  random battle folder.
  """
  keyWait
    any = false
  end
}

script 6 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder A!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 7 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder B!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 8 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder C!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 9 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder D!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 10 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder E!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 11 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder F!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 12 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder G!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 13 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder H!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 14 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder J!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 15 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder K!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 16 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder L!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 17 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder M!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 18 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder N!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 19 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder O!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 20 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder P!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 21 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder Q!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 22 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder R!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 23 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder S!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 24 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder T!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 25 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder U!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 26 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder V!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 27 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder W!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 28 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder X!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 29 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder Y!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 30 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder Z!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 31 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder a!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 32 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder b!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 33 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder c!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 34 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder d!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 35 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder e!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 36 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder f!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 37 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder g!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 38 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder h!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 39 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder i!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 40 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder j!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 41 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder k!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 42 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder m!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 43 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder n!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 44 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder o!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 45 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder p!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 46 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder q!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 47 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder r!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 48 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder s!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 49 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder t!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 50 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder u!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 51 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder v!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 52 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder w!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 53 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder x!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 54 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder y!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 55 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder z!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 56 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder 0!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 57 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder 1!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 58 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder 2!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 59 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder 3!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 60 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder 4!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 61 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder 5!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 62 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder 6!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 63 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder 7!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 64 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder 8!
  """
  keyWait
    any = false
  clearMsg
  end
}

script 65 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Chose Random Battle
  Folder 9!
  """
  keyWait
    any = false
  clearMsg
  end
}
