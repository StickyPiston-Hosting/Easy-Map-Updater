# Setup effect simulation

scoreboard players operation @s effect.levitation_duration = #duration effect.value
scoreboard players operation @s effect.levitation_amplifier = #amplifier effect.value

# Attribute formula: (level - 255)*0.9*0.05/49

execute if score #amplifier effect.value matches 128 run attribute @s minecraft:generic.gravity base set 0.11663265306122449
execute if score #amplifier effect.value matches 129 run attribute @s minecraft:generic.gravity base set 0.11571428571428573
execute if score #amplifier effect.value matches 130 run attribute @s minecraft:generic.gravity base set 0.11479591836734694
execute if score #amplifier effect.value matches 131 run attribute @s minecraft:generic.gravity base set 0.11387755102040818
execute if score #amplifier effect.value matches 132 run attribute @s minecraft:generic.gravity base set 0.1129591836734694
execute if score #amplifier effect.value matches 133 run attribute @s minecraft:generic.gravity base set 0.11204081632653062
execute if score #amplifier effect.value matches 134 run attribute @s minecraft:generic.gravity base set 0.11112244897959184
execute if score #amplifier effect.value matches 135 run attribute @s minecraft:generic.gravity base set 0.11020408163265306
execute if score #amplifier effect.value matches 136 run attribute @s minecraft:generic.gravity base set 0.10928571428571429
execute if score #amplifier effect.value matches 137 run attribute @s minecraft:generic.gravity base set 0.10836734693877552
execute if score #amplifier effect.value matches 138 run attribute @s minecraft:generic.gravity base set 0.10744897959183675
execute if score #amplifier effect.value matches 139 run attribute @s minecraft:generic.gravity base set 0.10653061224489797
execute if score #amplifier effect.value matches 140 run attribute @s minecraft:generic.gravity base set 0.1056122448979592
execute if score #amplifier effect.value matches 141 run attribute @s minecraft:generic.gravity base set 0.10469387755102043
execute if score #amplifier effect.value matches 142 run attribute @s minecraft:generic.gravity base set 0.10377551020408166
execute if score #amplifier effect.value matches 143 run attribute @s minecraft:generic.gravity base set 0.10285714285714286
execute if score #amplifier effect.value matches 144 run attribute @s minecraft:generic.gravity base set 0.1019387755102041
execute if score #amplifier effect.value matches 145 run attribute @s minecraft:generic.gravity base set 0.10102040816326531
execute if score #amplifier effect.value matches 146 run attribute @s minecraft:generic.gravity base set 0.10010204081632655
execute if score #amplifier effect.value matches 147 run attribute @s minecraft:generic.gravity base set 0.09918367346938776
execute if score #amplifier effect.value matches 148 run attribute @s minecraft:generic.gravity base set 0.09826530612244899
execute if score #amplifier effect.value matches 149 run attribute @s minecraft:generic.gravity base set 0.09734693877551022
execute if score #amplifier effect.value matches 150 run attribute @s minecraft:generic.gravity base set 0.09642857142857143
execute if score #amplifier effect.value matches 151 run attribute @s minecraft:generic.gravity base set 0.09551020408163266
execute if score #amplifier effect.value matches 152 run attribute @s minecraft:generic.gravity base set 0.09459183673469389
execute if score #amplifier effect.value matches 153 run attribute @s minecraft:generic.gravity base set 0.0936734693877551
execute if score #amplifier effect.value matches 154 run attribute @s minecraft:generic.gravity base set 0.09275510204081634
execute if score #amplifier effect.value matches 155 run attribute @s minecraft:generic.gravity base set 0.09183673469387756
execute if score #amplifier effect.value matches 156 run attribute @s minecraft:generic.gravity base set 0.0909183673469388
execute if score #amplifier effect.value matches 157 run attribute @s minecraft:generic.gravity base set 0.09
execute if score #amplifier effect.value matches 158 run attribute @s minecraft:generic.gravity base set 0.08908163265306122
execute if score #amplifier effect.value matches 159 run attribute @s minecraft:generic.gravity base set 0.08816326530612245
execute if score #amplifier effect.value matches 160 run attribute @s minecraft:generic.gravity base set 0.08724489795918368
execute if score #amplifier effect.value matches 161 run attribute @s minecraft:generic.gravity base set 0.0863265306122449
execute if score #amplifier effect.value matches 162 run attribute @s minecraft:generic.gravity base set 0.08540816326530613
execute if score #amplifier effect.value matches 163 run attribute @s minecraft:generic.gravity base set 0.08448979591836735
execute if score #amplifier effect.value matches 164 run attribute @s minecraft:generic.gravity base set 0.08357142857142859
execute if score #amplifier effect.value matches 165 run attribute @s minecraft:generic.gravity base set 0.08265306122448979
execute if score #amplifier effect.value matches 166 run attribute @s minecraft:generic.gravity base set 0.08173469387755104
execute if score #amplifier effect.value matches 167 run attribute @s minecraft:generic.gravity base set 0.08081632653061226
execute if score #amplifier effect.value matches 168 run attribute @s minecraft:generic.gravity base set 0.07989795918367347
execute if score #amplifier effect.value matches 169 run attribute @s minecraft:generic.gravity base set 0.07897959183673471
execute if score #amplifier effect.value matches 170 run attribute @s minecraft:generic.gravity base set 0.07806122448979592
execute if score #amplifier effect.value matches 171 run attribute @s minecraft:generic.gravity base set 0.07714285714285715
execute if score #amplifier effect.value matches 172 run attribute @s minecraft:generic.gravity base set 0.07622448979591838
execute if score #amplifier effect.value matches 173 run attribute @s minecraft:generic.gravity base set 0.07530612244897959
execute if score #amplifier effect.value matches 174 run attribute @s minecraft:generic.gravity base set 0.07438775510204082
execute if score #amplifier effect.value matches 175 run attribute @s minecraft:generic.gravity base set 0.07346938775510205
execute if score #amplifier effect.value matches 176 run attribute @s minecraft:generic.gravity base set 0.07255102040816327
execute if score #amplifier effect.value matches 177 run attribute @s minecraft:generic.gravity base set 0.07163265306122449
execute if score #amplifier effect.value matches 178 run attribute @s minecraft:generic.gravity base set 0.07071428571428572
execute if score #amplifier effect.value matches 179 run attribute @s minecraft:generic.gravity base set 0.06979591836734694
execute if score #amplifier effect.value matches 180 run attribute @s minecraft:generic.gravity base set 0.06887755102040816
execute if score #amplifier effect.value matches 181 run attribute @s minecraft:generic.gravity base set 0.0679591836734694
execute if score #amplifier effect.value matches 182 run attribute @s minecraft:generic.gravity base set 0.06704081632653061
execute if score #amplifier effect.value matches 183 run attribute @s minecraft:generic.gravity base set 0.06612244897959184
execute if score #amplifier effect.value matches 184 run attribute @s minecraft:generic.gravity base set 0.06520408163265307
execute if score #amplifier effect.value matches 185 run attribute @s minecraft:generic.gravity base set 0.0642857142857143
execute if score #amplifier effect.value matches 186 run attribute @s minecraft:generic.gravity base set 0.06336734693877552
execute if score #amplifier effect.value matches 187 run attribute @s minecraft:generic.gravity base set 0.06244897959183675
execute if score #amplifier effect.value matches 188 run attribute @s minecraft:generic.gravity base set 0.06153061224489797
execute if score #amplifier effect.value matches 189 run attribute @s minecraft:generic.gravity base set 0.06061224489795919
execute if score #amplifier effect.value matches 190 run attribute @s minecraft:generic.gravity base set 0.059693877551020416
execute if score #amplifier effect.value matches 191 run attribute @s minecraft:generic.gravity base set 0.05877551020408164
execute if score #amplifier effect.value matches 192 run attribute @s minecraft:generic.gravity base set 0.057857142857142864
execute if score #amplifier effect.value matches 193 run attribute @s minecraft:generic.gravity base set 0.05693877551020409
execute if score #amplifier effect.value matches 194 run attribute @s minecraft:generic.gravity base set 0.05602040816326531
execute if score #amplifier effect.value matches 195 run attribute @s minecraft:generic.gravity base set 0.05510204081632653
execute if score #amplifier effect.value matches 196 run attribute @s minecraft:generic.gravity base set 0.05418367346938776
execute if score #amplifier effect.value matches 197 run attribute @s minecraft:generic.gravity base set 0.05326530612244899
execute if score #amplifier effect.value matches 198 run attribute @s minecraft:generic.gravity base set 0.052346938775510214
execute if score #amplifier effect.value matches 199 run attribute @s minecraft:generic.gravity base set 0.05142857142857143
execute if score #amplifier effect.value matches 200 run attribute @s minecraft:generic.gravity base set 0.050510204081632655
execute if score #amplifier effect.value matches 201 run attribute @s minecraft:generic.gravity base set 0.04959183673469388
execute if score #amplifier effect.value matches 202 run attribute @s minecraft:generic.gravity base set 0.04867346938775511
execute if score #amplifier effect.value matches 203 run attribute @s minecraft:generic.gravity base set 0.04775510204081633
execute if score #amplifier effect.value matches 204 run attribute @s minecraft:generic.gravity base set 0.04683673469387755
execute if score #amplifier effect.value matches 205 run attribute @s minecraft:generic.gravity base set 0.04591836734693878
execute if score #amplifier effect.value matches 206 run attribute @s minecraft:generic.gravity base set 0.045
execute if score #amplifier effect.value matches 207 run attribute @s minecraft:generic.gravity base set 0.044081632653061226
execute if score #amplifier effect.value matches 208 run attribute @s minecraft:generic.gravity base set 0.04316326530612245
execute if score #amplifier effect.value matches 209 run attribute @s minecraft:generic.gravity base set 0.04224489795918367
execute if score #amplifier effect.value matches 210 run attribute @s minecraft:generic.gravity base set 0.041326530612244894
execute if score #amplifier effect.value matches 211 run attribute @s minecraft:generic.gravity base set 0.04040816326530613
execute if score #amplifier effect.value matches 212 run attribute @s minecraft:generic.gravity base set 0.039489795918367356
execute if score #amplifier effect.value matches 213 run attribute @s minecraft:generic.gravity base set 0.038571428571428576
execute if score #amplifier effect.value matches 214 run attribute @s minecraft:generic.gravity base set 0.037653061224489796
execute if score #amplifier effect.value matches 215 run attribute @s minecraft:generic.gravity base set 0.036734693877551024
execute if score #amplifier effect.value matches 216 run attribute @s minecraft:generic.gravity base set 0.035816326530612244
execute if score #amplifier effect.value matches 217 run attribute @s minecraft:generic.gravity base set 0.03489795918367347
execute if score #amplifier effect.value matches 218 run attribute @s minecraft:generic.gravity base set 0.0339795918367347
execute if score #amplifier effect.value matches 219 run attribute @s minecraft:generic.gravity base set 0.03306122448979592
execute if score #amplifier effect.value matches 220 run attribute @s minecraft:generic.gravity base set 0.03214285714285715
execute if score #amplifier effect.value matches 221 run attribute @s minecraft:generic.gravity base set 0.031224489795918374
execute if score #amplifier effect.value matches 222 run attribute @s minecraft:generic.gravity base set 0.030306122448979594
execute if score #amplifier effect.value matches 223 run attribute @s minecraft:generic.gravity base set 0.02938775510204082
execute if score #amplifier effect.value matches 224 run attribute @s minecraft:generic.gravity base set 0.028469387755102046
execute if score #amplifier effect.value matches 225 run attribute @s minecraft:generic.gravity base set 0.027551020408163266
execute if score #amplifier effect.value matches 226 run attribute @s minecraft:generic.gravity base set 0.026632653061224493
execute if score #amplifier effect.value matches 227 run attribute @s minecraft:generic.gravity base set 0.025714285714285714
execute if score #amplifier effect.value matches 228 run attribute @s minecraft:generic.gravity base set 0.02479591836734694
execute if score #amplifier effect.value matches 229 run attribute @s minecraft:generic.gravity base set 0.023877551020408165
execute if score #amplifier effect.value matches 230 run attribute @s minecraft:generic.gravity base set 0.02295918367346939
execute if score #amplifier effect.value matches 231 run attribute @s minecraft:generic.gravity base set 0.022040816326530613
execute if score #amplifier effect.value matches 232 run attribute @s minecraft:generic.gravity base set 0.021122448979591837
execute if score #amplifier effect.value matches 233 run attribute @s minecraft:generic.gravity base set 0.020204081632653064
execute if score #amplifier effect.value matches 234 run attribute @s minecraft:generic.gravity base set 0.019285714285714288
execute if score #amplifier effect.value matches 235 run attribute @s minecraft:generic.gravity base set 0.018367346938775512
execute if score #amplifier effect.value matches 236 run attribute @s minecraft:generic.gravity base set 0.017448979591836736
execute if score #amplifier effect.value matches 237 run attribute @s minecraft:generic.gravity base set 0.01653061224489796
execute if score #amplifier effect.value matches 238 run attribute @s minecraft:generic.gravity base set 0.015612244897959187
execute if score #amplifier effect.value matches 239 run attribute @s minecraft:generic.gravity base set 0.01469387755102041
execute if score #amplifier effect.value matches 240 run attribute @s minecraft:generic.gravity base set 0.013775510204081633
execute if score #amplifier effect.value matches 241 run attribute @s minecraft:generic.gravity base set 0.012857142857142857
execute if score #amplifier effect.value matches 242 run attribute @s minecraft:generic.gravity base set 0.011938775510204083
execute if score #amplifier effect.value matches 243 run attribute @s minecraft:generic.gravity base set 0.011020408163265306
execute if score #amplifier effect.value matches 244 run attribute @s minecraft:generic.gravity base set 0.010102040816326532
execute if score #amplifier effect.value matches 245 run attribute @s minecraft:generic.gravity base set 0.009183673469387756
execute if score #amplifier effect.value matches 246 run attribute @s minecraft:generic.gravity base set 0.00826530612244898
execute if score #amplifier effect.value matches 247 run attribute @s minecraft:generic.gravity base set 0.007346938775510205
execute if score #amplifier effect.value matches 248 run attribute @s minecraft:generic.gravity base set 0.0064285714285714285
execute if score #amplifier effect.value matches 249 run attribute @s minecraft:generic.gravity base set 0.005510204081632653
execute if score #amplifier effect.value matches 250 run attribute @s minecraft:generic.gravity base set 0.004591836734693878
execute if score #amplifier effect.value matches 251 run attribute @s minecraft:generic.gravity base set 0.0036734693877551023
execute if score #amplifier effect.value matches 252 run attribute @s minecraft:generic.gravity base set 0.0027551020408163266
execute if score #amplifier effect.value matches 253 run attribute @s minecraft:generic.gravity base set 0.0018367346938775511
execute if score #amplifier effect.value matches 254 run attribute @s minecraft:generic.gravity base set 0.0009183673469387756
execute if score #amplifier effect.value matches 255 run attribute @s minecraft:generic.gravity base set 0.0