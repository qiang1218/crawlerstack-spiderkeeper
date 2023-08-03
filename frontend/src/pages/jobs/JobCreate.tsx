import {
    BooleanInput,
    Create,
    SimpleForm,
    TextInput,
    ReferenceInput,
    SelectInput,
    NumberInput,
} from "react-admin";
import React from "react";
import { CPULimitValidate, MemoryLimitValidate } from "./JobParameValidate";
import { Box } from "@mui/material";

export const JobCreate = () => {
    return (
        <Box maxWidth="60em">
            <Create redirect="list" title="Create Job">
                <SimpleForm>
                    <TextInput
                        name="name"
                        source="name"
                        variant="outlined"
                        isRequired
                        label="Job名称"
                    />
                    <TextInput
                        name="cmdline"
                        source="cmdline"
                        variant="outlined"
                        isRequired
                        label="任务运行参数"
                        multiline
                        rows={2}
                        helperText="Examples: cmd api -p 80:80 -v ...(命令参数之间使用空格分割)"
                        fullWidth
                    />
                    <TextInput
                        name="environment"
                        source="environment"
                        variant="outlined"
                        multiline
                        helperText='多个环境变量之间使用 ";" 分号分割 Examples: a=b;a=b'
                        label="任务运行环境变量参数"
                        fullWidth
                        rows={3}
                    />
                    {/* a=b */}
                    <TextInput
                        name="volume"
                        source="volume"
                        variant="outlined"
                        defaultValue={null}
                        multiline
                        helperText='参数应为系统环境中有效路径，多个挂载参数使用 ";" 分号分割 Examples: " /tmp/foo:/tmp/bar;/tmp/test:/ " '
                        label="任务运行挂载参数"
                        fullWidth
                        rows={3}
                    />
                    {/* ; /n */}
                    <TextInput
                        name="trigger_expression"
                        source="trigger_expression"
                        variant="outlined"
                        isRequired
                        label="触发器表达式"
                        helperText="Examples: @daily or 0 0 0 0 0 （minutes hours days months years）"
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
                    <BooleanInput
                        name="storage_enable"
                        source="storage_enable"
                        variant="outlined"
                        label="是否开启存储"
                        defaultValue={false}
                    />
                    <ReferenceInput
                        name={"storage_server_id"}
                        label="storage server id"
                        source="storage_server_id"
                        reference="storage_servers"
                    >
                        <SelectInput
                            source="storage_server_id"
                            name="storage_server_id"
                            variant="outlined"
                            optionText="name"
                            optionValue="id"
                        />
                    </ReferenceInput>
                    <BooleanInput
                        name="snapshot_enable"
                        source="snapshot_enable"
                        variant="outlined"
                        label="是否开启快照"
                        defaultValue={false}
                    />
                    <ReferenceInput
                        name="snapshot_server_id"
                        label="snapshot server id"
                        source="snapshot_server_id"
                        reference="storage_servers"
                    >
                        <SelectInput
                            source="snapshot_server_id"
                            name="snapshot_server_id"
                            variant="outlined"
                            optionText="name"
                            optionValue="id"
                        />
                    </ReferenceInput>

                    <TextInput
                        name="executor_selector"
                        variant="outlined"
                        source="executor_selector"
                        isRequired
                        defaultValue="latest"
                        label="执行器选择器"
                    />
                    <ReferenceInput
                        name="artifact_id"
                        variant="outlined"
                        label="artifact id"
                        source="artifact_id"
                        reference="artifacts"
                    >
                        <SelectInput
                            source="artifact_id"
                            name="artifact_id"
                            variant="outlined"
                            optionText="name"
                            optionValue="id"
                            resettable
                        />
                    </ReferenceInput>
                </SimpleForm>
            </Create>
        </Box>
    );
};

export default JobCreate;
