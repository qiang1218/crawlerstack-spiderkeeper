import { AutocompleteInput, ReferenceInput } from "react-admin";
import React from "react";

export const tasksFilters = [
    <ReferenceInput
        name="job_id"
        source="job_id"
        reference="jobs"
        variant="outlined"
    >
        <AutocompleteInput
            name="job_id"
            source="job_id"
            optionText="name"
            variant="outlined"
            sx={{ width: 300 }}
            label="作业Id"
        />
    </ReferenceInput>,
];

export const jobsFilters = [
    <ReferenceInput
        name="executors_type"
        source="executors_type"
        reference="executors"
        label="执行器类型"
    >
        <AutocompleteInput
            source="executor_type"
            name="executor_type"
            label="执行器类型"
            variant="outlined"
            isRequired
            optionText="type"
            optionValue="type"
        />
    </ReferenceInput>,
    <ReferenceInput
        name="artifact_id"
        source="artifact_id"
        reference="artifacts"
        variant="outlined"
    >
        <AutocompleteInput
            name="artifact_id"
            source="artifact_id"
            optionText="name"
            variant="outlined"
            sx={{ width: 300 }}
            label="所属归档"
        />
    </ReferenceInput>,
];
