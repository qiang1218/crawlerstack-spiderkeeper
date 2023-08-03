import {
    DateField,
    NumberField,
    TextField,
    List,
    DatagridConfigurable,
} from "react-admin";
import { ListTopToolbar } from "../ActionsToolbar";
import React from "react";

export const ProjectsList = () => (
    <List actions={<ListTopToolbar />}>
        <DatagridConfigurable rowClick="edit" bulkActionButtons={false}>
            <TextField source="id" label="ID" />
            <TextField source="name" label="项目名称" />
            <TextField
                source="desc"
                label="项目描述"
                maxHeight={1}
                maxWidth={1}
            />
            <DateField
                source="create_time"
                label="创建时间"
                defaultChecked={false}
                showTime
            />
            <DateField
                source="update_time"
                label="更新时间"
                defaultChecked={false}
                showTime
            />
        </DatagridConfigurable>
    </List>
);

export default ProjectsList;
