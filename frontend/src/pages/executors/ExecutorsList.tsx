import {
    DateField,
    List,
    NumberField,
    TextField,
    UrlField,
    SelectField,
    DatagridConfigurable,
} from "react-admin";
import { Status } from "../../constant";
import React from "react";
import { GeneralTopToolbar } from "../ActionsToolbar";

export const ExecutorList = () => (
    <List actions={<GeneralTopToolbar />}>
        <DatagridConfigurable bulkActionButtons={false}>
            <TextField source="id" />
            <TextField source="name" label="执行器" />
            <TextField source="selector" label="选择器" />
            <UrlField source="url" label="执行器地址" />
            <TextField source="type" label="执行器类型" />
            <SelectField
                source="status"
                label="状态"
                choices={Status}
                align="center"
            />
            <TextField source="memory" label="内存" align="right" />
            <NumberField source="cpu" label="CPU" />
            <NumberField source="task_count" label="任务数量" />
            <DateField source="update_time" label="更新时间" showTime />
            <DateField source="create_time" label="创建时间" showTime />
        </DatagridConfigurable>
    </List>
);

export default ExecutorList;
