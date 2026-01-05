import { Temporal } from "@js-temporal/polyfill";
import { useEffect, useState } from "react";

import APICall from "scripts/api.ts";

interface PersonnelData {
  id: string;
  first_name: string;
  last_name: string;
  created_at: Temporal.Instant;
  updated_at: Temporal.Instant;
}

function WelcomeText() {
  const [personnel, setPersonnel] = useState<PersonnelData>();

  useEffect(() => {
    async function fetchPersonnel() {
      const [q, w, e] = await APICall.put("/personal/select", {
        id: "43eb1880-c4a2-4948-a91b-b6f8181f6933",
      });

      console.log(q, w, e);

      const [success, response, message] = await APICall.get<PersonnelData>(
        "/personal/me"
      );

      if (success) {
        setPersonnel(response!);
      } else {
        console.log("Error when getting data");
        console.log(message);
      }
    }
    fetchPersonnel();
  }, []);

  if (!personnel) return <h1>No Person Set</h1>;

  return <h1>Welcome Back {personnel.first_name}</h1>;
}

export default WelcomeText;
