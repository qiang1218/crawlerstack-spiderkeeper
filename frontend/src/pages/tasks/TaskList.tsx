import {
    DateField,
    List,
    ReferenceField,
    SelectField,
    Tab,
    TextField,
    DatagridConfigurable,
    TopToolbar,
    FilterButton,
} from "react-admin";
import React from "react";
import { Status } from "../../constant";
import { ButtonGroup } from "@mui/material";
import { TaskStartButton } from "../../components/buttons/TaskStartButton";
import { TaskStopButton } from "../../components/buttons/TaskStopButton";
import { TaskTerminateButton } from "../../components/buttons/TaskTerminateButton";
import { SelectColumnItem } from "../../components/buttons/styles";
import { tasksFilters } from "../Filters";

export const TaskList = () => {
    return (
        <List
            filters={tasksFilters}
            actions={
                <TopToolbar>
                    <FilterButton defaultValue={[]} />
                    <SelectColumnItem />
                </TopToolbar>
            }
            sort={{ field: "update_time", order: "DESC" }}
            perPage={10}
        >
            <DatagridConfigurable bulkActionButtons={false}>
                <TextField source="id" label="ID" />
                <TextField source="name" label="任务名称" />
                <DateField source="update_time" label="Last Run" showTime />
                <ReferenceField
                    source="job_id"
                    label="所属作业"
                    reference="jobs"
                >
                    <TextField source={"name"} />
                </ReferenceField>
                <SelectField
                    source="task_status"
                    choices={Status}
                    fontSize="small"
                    textAlign="center"
                    label="任务状态"
                />
                <SelectField
                    source="consume_status"
                    choices={Status}
                    fontSize="small"
                    textAlign="center"
                    label="消费状态"
                />
                <Tab label="任务消费操作">
                    <ButtonGroup variant="text">
                        <TaskStartButton />
                        <TaskStopButton />
                        <TaskTerminateButton />
                    </ButtonGroup>
                </Tab>
            </DatagridConfigurable>
        </List>
    );
};

export default TaskList;
