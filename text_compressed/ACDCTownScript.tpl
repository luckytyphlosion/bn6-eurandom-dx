@archive ACDCTownScript
@size 2

script 0 mmbn6 {
  msgOpen
  itemGiveAllChips
  """
  Welcome to the BN6
  Random Battle patch!
  """
  keyWait
    any = false
  clearMsg

  """
  To pick a folder, just
  press L and choose the
  folder!
  """
  keyWait
    any = false
  clearMsg

  """
  Remember to set your
  reg and tag before
  the match!
  """
  keyWait
    any = false
  clearMsg

  """
  And for those interested,
  the source code for this
  patch can be found at:
  """
  keyWait
    any = false
  clearMsg

  """
  github.com/luckytyphlosion/bn6-eurandom-dx
  """
  keyWait
    any = false
  end
}

script 1 mmbn6 {
  flagSet
    flag = 0x403
  end
}
