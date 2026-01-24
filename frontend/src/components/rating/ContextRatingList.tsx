import { useState } from "react";

import RatingList from "components/rating/RatingList";
import UpdateRating from "components/rating/UpdateRating";

import { ContextRefreshList } from "contexts/ContextRefreshList";

function ContextRatingList() {
  const [refreshList, setRefreshList] = useState(true);

  return (
    <ContextRefreshList.Provider value={{ refreshList, setRefreshList }}>
      <UpdateRating />
      <RatingList />
    </ContextRefreshList.Provider>
  );
}

export default ContextRatingList;
