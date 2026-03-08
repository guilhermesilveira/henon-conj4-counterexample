import Lake
open Lake DSL

package "henon-pub15" where
  version := v!"0.1.0"
  keywords := #["math", "henon", "arithmetic-dynamics", "formalization", "period-3"]
  leanOptions := #[
    ⟨`pp.unicode.fun, true⟩
  ]

require "leanprover-community" / "mathlib"

@[default_target]
lean_lib «HenonPub15» where

require checkdecls from git "https://github.com/PatrickMassot/checkdecls.git"

meta if get_config? env = some "dev" then
require «doc-gen4» from git
  "https://github.com/leanprover/doc-gen4" @ "main"
