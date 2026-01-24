import { useState } from "react";

import CreatePersonnel from "components/personnel/CreatePersonnel";
import PersonnelList from "components/personnel/PersonnelList";

import { ContextRefreshPersonnelList } from "contexts/ContextRefreshPersonnelList";

function ContextPersonnelList() {
  const [refreshList, setRefreshList] = useState(true);

  return (
    <ContextRefreshPersonnelList.Provider
      value={{ refreshList, setRefreshList }}
    >
      <CreatePersonnel />
      <PersonnelList />
    </ContextRefreshPersonnelList.Provider>
  );
}

export default ContextPersonnelList;
