@archive RandomBattleFolderNotSetProperlyTextScript
@size 4

script 0 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  You didn't set your
  random battle folder!
  """
  keyWait
    any = false
  clearMsg

  """
  Opponent's folder is:
  "
  """

  printBufferedShortString
    bufferOffset = 0

  """
  ".
  """
  waitHold
}

script 1 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  Your opponent didn't
  set their random
  battle folder!
  """
  keyWait
    any = false
  clearMsg

  """
  Your folder is:
  "
  """

  printBufferedShortString
    bufferOffset = 0

  """
  ".
  """
  waitHold
}

script 2 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  You and your opponent
  did not set your
  random battle folders!
  """
  waitHold
}

script 3 mmbn6 {
  mugshotShow
    mugshot = MegaMan
  msgOpen
  """
  You are not using the
  same folder as your
  opponent!
  """
  keyWait
    any = false
  clearMsg

  "Your folder:\""
  printBufferedShortString
    bufferOffset = 0

  "\"\n"
  "Opponent's folder:\""
  printBufferedShortString
    bufferOffset = 4
  "\""

  waitHold
}

