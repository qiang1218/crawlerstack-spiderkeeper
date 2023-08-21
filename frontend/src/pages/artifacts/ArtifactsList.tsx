import {
    DatagridConfigurable,
    DateField,
    List,
    ReferenceField,
    TextField,
} from "react-admin";
import React from "react";
import { ListTopToolbar } from "../ActionsToolbar";

export const ArtifactList = () => (
    <List actions={<ListTopToolbar />} perPage={10}>
        <DatagridConfigurable rowClick="edit" bulkActionButtons={false}>
            <TextField source="id" label="ID" />
            <TextField source="name" label="归档名称" />
            <TextField source="desc" label="归档描述" />
            <TextField source="image" label="镜像名称" />
            <TextField source="tag" label="归档标签" />
            <TextField source="version" label="镜像版本" />
            <ReferenceField
                source="project_id"
                reference="projects"
                label="所属项目"
            >
                <TextField source={"name"} />
            </ReferenceField>
            <DateField source="create_time" label="创建时间" showTime />
            <DateField source="update_time" label="更新时间" showTime />
        </DatagridConfigurable>
    </List>
);

export default ArtifactList;
