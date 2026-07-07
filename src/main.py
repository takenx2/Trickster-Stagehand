import transfer,tricks,metafragments,fragments

read = input("ENTER FRAGMENT > ")

fragment = transfer.decompress_fragment(read)
if isinstance(fragment,metafragments.SpellPart):
    tricks.say(fragment)
    fragment=fragment.run_glyph()
tricks.say(fragment)