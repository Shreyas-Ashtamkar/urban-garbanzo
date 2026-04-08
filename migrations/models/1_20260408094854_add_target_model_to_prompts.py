from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "prompts" ADD "target_model" VARCHAR(256) NOT NULL DEFAULT 'unknown';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "prompts" DROP COLUMN "target_model";"""


MODELS_STATE = (
    "eJztmm1v4jgQgP+K5U9dqYdaCuwKnU6ilN6y28KqpXerPZ0iE5tg1bGp7bRFvf73k52EvB"
    "AoydEtPfGlKmOPEz8z8bzIT9AXmDBV690jFiBNBYdt8AQ58glsg4LRQwDRbJaMGYFGY2an"
    "k8U8K0djpSVyNWyDCWKKHAKIiXIlnUUPgtdaSIJBogeUKyRRYCIkQGAmhT/TNbMWFq7Skn"
    "KvnFrA6V1AHC08oqdEwjb46+9DACnH5JGo+Ofs1plQwnBm7xSbBazc0fOZld3c9M/O7Uzz"
    "SmPHFSzweTJ7NtdTwRfTg4DimtExYx7hRCJNcAoHDxiL4MWi8I1hG2gZkMWr4kSAyQQFzE"
    "CFv04C7tr92yeZP43f4BJm85QcwkjkCm5MRLk2LJ6ew10le7ZSaB7V/dy5OjhpfbC7FEp7"
    "0g5aIvDZKiKNQlXLNQHpMiSpni/TPCMu9RErBprSylHFoVotUq/CNhYkcBMHjenG1LaO8q"
    "zX7V92Lg6ah3WLU90xqu3O/uhcWc6Now+WaYqhkJK4mhOlynLMau5ZQsonQvr23HAw4aq8"
    "b65YYc8WThFjgUt5yEZSdVsSbfECe7JQEhxwjLhb1lmzinuSUAuNmGMzhpIoc5p7lnBKAk"
    "mVpm5IpSA4fbkeDlZ86gW6eaTU1eAfwKjSr4UzlUSNA8o05apmHvtKeZTBYVb2lbpjRjCI"
    "4V52vlvsQiI3TKcH3YvhaT7hMguc5qzAmF+Bf1ZrT74KeWnjFGIFJ8mIPOoVJ3JaKcddab"
    "kB76gU2I1zY9T7PloP1p9HIxfDwe/x9DztZZeeSXFPMZHLbLtTJFc7dVqvEt5q7swFtxat"
    "SBj66NFhhHt6CtvgpL6GeMz3JDyoUySjkbodyhKNqmWCHaQL4h7SRFOfFFPN6+YPi0i5Fv"
    "+zm7EPSoLwkLN59AWt8+n+Ze961Ln8lnHss86oZ0bqGaeOpQetnDUWi4A/+6PPwPwEP4aD"
    "Xv5gWcwb/YDmnVCghcPFg4Nwqu6PpTGYjHHDlodTrmeRUdpm6+JNj6MXOhWm3zO5LWxUhD"
    "yWCZ4LSajHv5K55djnSiPuFp3eUb/s22KhnSWXSBMPk+hh0QfLOoetcxkJs8Fu57rbOetB"
    "i3KM3NsHJLGTYWpGRF3kJIu5y0N+3c9LEEeeJWD2Yd46C7egTZlgX92iDLe1aXsyGPtUa4"
    "KjliLQ5FED9ICoptxL9R8LWpSlVPdtyrdvUxoDlcni4vk/L8N4XxmcRtIj2rHfYJkMLq/3"
    "Xvhm87d6s7VBAldvtlZmcHYs1wWWpGICl9Xcp287lr4FM1zRsFnNvWHf1LDRyyd2DZOmKn"
    "bNam7BrrvVMtghM8bbXv+BKiJLVlcplf+Qb+2U2aqXVgbGFgqrm2iZXYX2YlWVcopMTXXd"
    "G4HBzcXFuqJqqZUT37PIQj2NlM+/XhG2uLRRzDN7sWP3IsMqrM+vWWBaJysoL2PnW11cGu"
    "tuWFp2uOBzXwQKTBHHjIBAEQy0AJ4UwSwuGpWpIpUyhl4uMastsS81d6DURF65isjbXiH0"
    "MsRtlkGtxgZVUKuxsggyQ/sa6H+YKocp1lLGsEn0S7Xwqke+jVu0u5NLvGrQ6xBJ3WlR2I"
    "tG1gY+lMx5KfKtxrDlyNTnukRgMphzzhBZ/k0PU8885Zf6ceNj49NJq/HpEED7JgvJxzUn"
    "QH8weiEQ3RNpMoMywSil8l47c82NOnPNNZ25Zj4qmU+jBMRo+vsEeHx0tAHA46OjlQDtWP"
    "6CK9ck/AY3vb+SUvn5l1dercb+sq1rKiVi6/YDy/O/9HemBg=="
)
