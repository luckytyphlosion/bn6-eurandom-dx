@archive LoadNewGameSaveTextScript
@size 1

script 0 mmbn6 {
  msgOpen
  """
  This patch only works
  with a new save.
  """
  keyWait
    any = false
  clearMsg

  """
  Please reset and start
  from a new game.
  """
  waitHold
}
