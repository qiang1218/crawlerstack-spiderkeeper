import {
    Edit,
    ReferenceInput,
    SimpleForm,
    TextInput,
    SelectInput,
    useRecordContext,
    BooleanInput,
    NumberInput,
} from "react-admin";
import React from "react";
import { CPULimitValidate, MemoryLimitValidate } from "./JobParameValidate";
import { EditTopToolbar } from "../ActionsToolbar";
import { Box } from "@mui/material";

const PageTitle = () => {
    const record: any = useRecordContext();
    return <span>{record ? `"${record.name}" 作业` : ""}</span>;
};

export const JobEdit = () => (
    <Box maxWidth="65em">
        <Edit title={<PageTitle />} actions={<EditTopToolbar />}>
            <SimpleForm>
                <TextInput
                    name="id"
                    variant="outlined"
                    label="Id"
                    source="id"
                    disabled
                />
                <TextInput name="name" variant="outlined" source="name" />
                <TextInput
                    name="cmdline"
                    variant="outlined"
                    source="cmdline"
                    label="任务运行参数"
                    fullWidth
                    multiline
                    rows={2}
                />
                <TextInput
                    name="environment"
                    variant="outlined"
                    source="environment"
                    multiline
                    rows={3}
                    label="任务运行环境变量参数"
                    fullWidth
                />
                <TextInput
                    name="volume"
                    variant="outlined"
                    source="volume"
                    label="任务运行挂载参数"
                    multiline
                    rows={2}
                    fullWidth
                />
                <TextInput
                    name="trigger_expression"
                    variant="outlined"
                    source="trigger_expression"
                    label="触发器表达式"
                />
                <ReferenceInput
                    name="executors_type"
                    source="executors_type"
                    reference="executors"
                >
                    <SelectInput
                        source="executor_type"
                        name="executor_type"
                        label="执行器类型"
                        variant="outlined"
                        isRequired
                        optionText="type"
                        optionValue="type"
                    />
                </ReferenceInput>
                <NumberInput
                    name="cpu_limit"
                    source="cpu_limit"
                    variant="outlined"
                    label="CPU限制/millicores"
                    helperText="资源上限cpu核心数以 millicores 微核为单位"
                    defaultValue={200}
                    validate={CPULimitValidate}
                />
                <NumberInput
                    name="memory_limit"
                    source="memory_limit"
                    variant="outlined"
                    label="资源上限内存大小"
                    helperText="资源上限内存大小以 MB 为单位"
                    defaultValue={1024}
                    validate={MemoryLimitValidate}
                />
                <ReferenceInput
                    name={"artifact_id"}
                    variant="outlined"
                    source="artifact_id"
                    reference="artifacts"
                >
                    <SelectInput
                        source="artifact_id"
                        name="artifact_id"
                        variant="outlined"
                        optionText="name"
                        optionValue="id"
                        label="选择归档模式"
                        resettable
                    />
                </ReferenceInput>
                <TextInput
                    name="executor_type"
                    variant="outlined"
                    source="executor_type"
                    label="执行器类型"
                />
                <TextInput
                    name="executor_selector"
                    variant="outlined"
                    source="executor_selector"
                    label="执行器选择器"
                />
                <BooleanInput
                    name="enabled"
                    source="enabled"
                    label="Job状态"
                    disabled
                />
                <BooleanInput name="pause" source="pause" disabled />
                <BooleanInput
                    name="storage_enable"
                    source="storage_enable"
                    label="是否开启存储"
                />
                <BooleanInput
                    name="snapshot_enable"
                    source="snapshot_enable"
                    variant="outlined"
                    label="是否开启快照"
                />
                <ReferenceInput
                    name="storage_server_id"
                    variant="outlined"
                    source="storage_server_id"
                    reference="storage_servers"
                >
                    <SelectInput
                        source="storage_server_id"
                        name="storage_server_id"
                        variant="outlined"
                        optionText="name"
                        optionValue="id"
                        defaultValue={null}
                        label="选择存储模式"
                        resettable
                    />
                </ReferenceInput>
            </SimpleForm>
        </Edit>
    </Box>
);

export default JobEdit;
