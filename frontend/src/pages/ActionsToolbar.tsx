import { TopToolbar } from "react-admin";
import {
    CreateItemButton,
    EditOneButton,
    SelectColumnItem,
    ShowOneButton,
} from "../components/buttons/styles";
import React from "react";
import AddCircleIcon from "@mui/icons-material/AddCircle";
export const ListTopToolbar = () => (
    <TopToolbar>
        <SelectColumnItem />
        <CreateItemButton icon={<AddCircleIcon />} />
    </TopToolbar>
);
export const ShowTopToolbar = () => (
    <TopToolbar>
        <EditOneButton />
    </TopToolbar>
);

export const EditTopToolbar = () => (
    <TopToolbar>
        <ShowOneButton />
    </TopToolbar>
);
export const GeneralTopToolbar = () => (
    <TopToolbar>
        <SelectColumnItem />
    </TopToolbar>
);
