import Lake
open Lake DSL
package «henon-core» where
require mathlib from git "https://github.com/leanprover-community/mathlib4.git" @ "3bad2b8ecd5b83c92c411251264c178763cd984c"
@[default_target]
lean_lib HenonPub15 where
