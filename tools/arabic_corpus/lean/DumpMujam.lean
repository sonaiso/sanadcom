import Jisr.AqsamAwamil

def kindStr : SLGE.Cat.Kind → String | .ism => "ism" | .fil => "fil" | .harf => "harf"

def kindsStr : Option (List SLGE.Cat.Kind) → String
  | none => "none"
  | some l => ",".intercalate (List.map kindStr l)

#eval do
  for (g, s, ks) in Jisr.AqsamAwamil.mujam2 do
    IO.println s!"{g}\t{s}\t{kindsStr ks}"
