import {
    ChipField,
    List,
    ReferenceField,
    SelectField,
    Tab,
    TextField,
    TopToolbar,
    Datagrid,
} from "react-admin";
import { ButtonGroup } from "@mui/material";
import React from "react";
import {
    PauseButton,
    RunButton,
    StartButton,
    StopButton,
    UnpauseButton,
} from "../../components/buttons";
import { Status } from "../../constant";
import { jobsFilters } from "../Filters";
import {
    CreateItemButton,
    FilterDropdownButton,
    SelectColumnItem,
} from "../../components/buttons/styles";
import AddCircleIcon from "@mui/icons-material/AddCircle";

const Toolbar = (
    <TopToolbar>
        <FilterDropdownButton />
        <SelectColumnItem />
        <CreateItemButton icon={<AddCircleIcon />} />
    </TopToolbar>
);

export const JobList = () => {
    return (
        <List actions={Toolbar} filters={jobsFilters}>
            <Datagrid rowClick="show">
                <TextField source="id" label="ID" />
                <TextField source="name" label="作业名称" />
                <ChipField source="trigger_expression" label="调度时间" />
                <TextField source="executor_type" label="执行器类型" />
                <ReferenceField
                    source="artifact_id"
                    reference="artifacts"
                    label="所属归档"
                    link={false}
                >
                    <TextField source="name" color="secondary" />
                </ReferenceField>
                <SelectField
                    source="storage_enable"
                    choices={Status}
                    label="启用/禁用数据存储"
                />
                <ReferenceField
                    source="storage_server_id"
                    reference="storage_servers"
                    label="数据存储配置"
                    link={false}
                >
                    <TextField source="name" color="secondary" />
                </ReferenceField>
                <SelectField
                    source="snapshot_enable"
                    choices={Status}
                    label="启用/禁用快照存储"
                />
                <ReferenceField
                    source="snapshot_server_id"
                    reference="storage_servers"
                    label="快照存储配置"
                    link={false}
                >
                    <TextField source="name" color="secondary" />
                </ReferenceField>
                <SelectField
                    source="enabled"
                    choices={Status}
                    label="启用/禁用定时任务"
                />
                <SelectField source="pause" choices={Status} label="暂停状态" />
                <Tab label="Actions">
                    <ButtonGroup variant="text">
                        <RunButton />
                        <StartButton />
                        <StopButton />
                        <PauseButton />
                        <UnpauseButton />
                    </ButtonGroup>
                </Tab>
            </Datagrid>
        </List>
    );
};

export default JobList;
