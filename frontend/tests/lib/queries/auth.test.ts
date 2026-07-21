import { describe, it } from "vitest"

import { PersonnelLogin } from "@/lib/interfaces/personnel"
import { personnelLoginQuery } from "@/lib/queries/auth"

describe ("personnelLoginQuery", () => {
    it("returns successful response", async () => {
        const data = { email: "test@email.com", password: "Password1." } as PersonnelLogin
        const response = await personnelLoginQuery(data)
    })
})
