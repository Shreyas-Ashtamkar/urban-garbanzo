from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID NOT NULL PRIMARY KEY,
    "tag" VARCHAR(64) NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "users" IS 'Anonymous handle used to group prompt submissions.';
CREATE TABLE IF NOT EXISTS "prompts" (
    "id" UUID NOT NULL PRIMARY KEY,
    "text" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "user_id" UUID REFERENCES "users" ("id") ON DELETE SET NULL
);
COMMENT ON TABLE "prompts" IS 'Submitted prompt text awaiting evaluation.';
CREATE TABLE IF NOT EXISTS "evaluations" (
    "id" UUID NOT NULL PRIMARY KEY,
    "clarity" DECIMAL(5,2) NOT NULL,
    "correctness" DECIMAL(5,2) NOT NULL,
    "information_density" DECIMAL(5,2) NOT NULL,
    "hallucination_risk" DECIMAL(5,2) NOT NULL,
    "redundancy" DECIMAL(5,2) NOT NULL,
    "total_score" DECIMAL(5,2) NOT NULL,
    "heuristic_scores" JSONB NOT NULL,
    "llm_scores" JSONB NOT NULL,
    "rationale" TEXT,
    "llm_provider" VARCHAR(32) NOT NULL DEFAULT 'none',
    "evaluated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "prompt_id" UUID NOT NULL REFERENCES "prompts" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "evaluations" IS 'Stored evaluation scores for a prompt.';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztmv9P2zgUwP8Vyz8xiaugFDZVp5NKKbduUCYot2nTKXJjt7Vw7GI7QMX43092kuZLk9"
    "JkZYRTf0H02c+JP+/F74v8CD2BCVON3h1iPtJUcNgGj5Ajj8A2yBndBRDNZvGYEWg0YnY6"
    "WcyzcjRSWiJXwzYYI6bILoCYKFfSWfggeKWFJBjEekC5QhIFxkICBGZSeDPdMGth4SotKZ"
    "+UU/M5vfWJo8WE6CmRsA1+/LsLIOWYPBAV/ZzdOGNKGE7tnWKzgJU7ej6zsuvr/smpnWle"
    "aeS4gvkej2fP5noq+GK671PcMDpmbEI4kUgTnMDBfcZCeJEoeGPYBlr6ZPGqOBZgMkY+M1"
    "Dhn2Ofu3b/9knmT+svuITZPCWDMBS5ghsTUa4Ni8enYFfxnq0Umkd1P3Yudw6O3tldCqUn"
    "0g5aIvDJKiKNAlXLNQbpMiSpni/TPCEu9RDLB5rQylDFgVojVK/CNhLEcGMHjehG1DaO8q"
    "TX7Z93znYOd5sWp7plVNud/dO5tJxbe+8s0wRDISVxNSdKleWY1tyyhJSPhfTsueFgwlV5"
    "3yxYYcsWThFjvkt5wEZSdVMSbf4CW7JQEuxzjLhb1lnTiluSUAuNmGMzhpIoM5pblnBKfE"
    "mVpm5AJSc4fbq6GBR86jm6WaTU1eAnYFTpl8KZSKJGPmWactUwj32hPMrgMCt7St0yIxhE"
    "cM873yx2IZEbpNOD7tnFcTbhMgscZ6zAmFeBf1prS74KeWnjFGI5J8mQPOiCEzmplOGutF"
    "yDd1gK1OPcGPa+DVeD9ebhyNnF4O9oepb2skvPpLijmMhltt0pksVOndSrhLeaO3PBrUUr"
    "EoYeenAY4RM9hW1w0FxBPOJ7EBzUCZLhSNMOpYmG1TLBDtI5cQ9poqlH8qlmdbOHRajciP"
    "6pZ+yDkiB8wdk8/IJW+XT/vHc17Jx/STn2SWfYMyPNlFNH0p2jjDUWi4Cv/eFHYH6C7xeD"
    "XvZgWcwbfofmnZCvhcPFvYNwou6PpBGYlHGDlodTrmeRUtpk6+JVj6NnOhWm3zO+yW1UBD"
    "yWCZ4KSeiEfyZzy7HPlUbczTu9w37Zl8VCtSUXS2MPk+h+0QdLO4etcxkJssFu56rbOelB"
    "i3KE3Jt7JLGTYmpGRFNkJIu5y0Ne08tKEEcTS8Dsw7x1Gm5OmzLGXtyiDLa1bnvSH3lUa4"
    "LDliLQ5EEDdI+opnyS6D/mtChLqW7blK/fpjQGKpPFRfN/X4bxtjI4V5KK2UZac5tr1CzX"
    "8Ge4omHTmlvDvqphw5eP7RpE+Cp2TWtuwK71qm9rZMZo26s/UEVkyVIgofILyUGtzFa9Dj"
    "AwNlAFXIfL1BXasyVAwilSBcBVbwgG12dnqyqApb5DdCkgDfU4VD79fEnY4oZBPs/0LYT6"
    "RYYirE8vWQ1ZJ8uphSLnK66EjHXXrIM6XPC5J3wFpohjRoCvCAZagIkU/iyqcJQpeZQyhl"
    "6uh6otsa2LalAXoUmZBmw4fTNV0fMQfzGZS/Vcj1pr9FyPWoU9VzO0rYH+h6lykGItZQzr"
    "RL9Ev6l65Fu7n1ifXOJFg16HSOpO88JeOLIy8KF4znORrxjDhiNTn+sSgclgzjhDaPlXPU"
    "wn5il/NPdb71sfDo5aH3YBtG+ykLxfcQL0B8NnAtEdkSYzKBOMEipvpU2XDknNw8M1YlLz"
    "8LAwKNmxdFQyn0YJiOH0twlwf29vDYD7e3uFAO1Y9jYm1yT4Bte9bJFQ+f03LV6sxv60qT"
    "sVJWLr5gPL03+mkzlX"
)
