import { useContext, useEffect, useState } from "react";

import { RankingTrackerContext } from "@/components/tracker/rateDayContext";
import { PersonnelProp } from "@/lib/interfaces/personnel";
import { getPersonnelQuery } from "@/lib/queries/personnel";

interface DisplayRankingTodayProps {}

export default function DisplayRankingToday({}: DisplayRankingTodayProps) {
  const { refreshRanking } = useContext(RankingTrackerContext);

  const [user, setUser] = useState<PersonnelProp>();

  useEffect(() => {
    async function get_personnel() {
      const result = await getPersonnelQuery();

      if (result.isOk()) {
        console.log("Success");
        console.log(result.value);
        setUser(result.value);
      } else {
        console.log("Error Occurred");
        console.log(result.error);
      }
    }

    get_personnel();
  }, []);

  return (
    <div>
      <h1>Welcome Back {user?.first_name}</h1>

      {refreshRanking.ranking != undefined ? (
        <h1>You have ranked today as a {refreshRanking.ranking}</h1>
      ) : (
        <h1>You have not yet ranked {refreshRanking.day}</h1>
      )}
    </div>
  );
}
