import { DataProvider } from "react-admin";
import { GetListResult, RaRecord } from "ra-core";

export interface ActionParams<RecordType extends RaRecord = any> {
    id: RecordType["id"];
    previousData?: RecordType;
    meta?: any;
}
export interface ActionRecord {
    message: string;
}

export interface ActionResult<RecordType extends ActionRecord = ActionRecord> {
    data: RecordType;
}

export interface LogParams {
    line: number;
    name: string;
    meta?: any;
}

export type LogRecord = string[];

export interface LogResult<RecordType extends LogRecord = any> {
    data: RecordType;
}

export interface UserRecord {
    name: string;
    nickname: string;
    email: string;
    picture: string;
}

export interface UsersResult<RecordType extends UserRecord = any> {
    data: RecordType;
}

export interface UserParams {
    session_id?: string;
}

export type LogoutRecord = string[];

export interface LogoutResult<RecordType extends LogoutRecord = any> {
    message: RecordType;
}

export interface JsonDataProviderType<ResourceType extends string = string>
    extends DataProvider {
    jobRun: <
        ParamsRecordType extends RaRecord = any,
        RecordType extends ActionRecord = ActionRecord
    >(
        resource: ResourceType,
        params: ActionParams<ParamsRecordType>
    ) => Promise<ActionResult<RecordType>>;
    jobStart: <
        ParamsRecordType extends RaRecord = any,
        RecordType extends ActionRecord = ActionRecord
    >(
        resource: ResourceType,
        params: ActionParams<ParamsRecordType>
    ) => Promise<ActionResult<RecordType>>;
    pause: <
        ParamsRecordType extends RaRecord = any,
        RecordType extends ActionRecord = any
    >(
        resource: ResourceType,
        params: ActionParams<ParamsRecordType>
    ) => Promise<ActionResult<RecordType>>;
    unpause: <
        ParamsRecordType extends RaRecord = any,
        RecordType extends ActionRecord = any
    >(
        resource: ResourceType,
        params: ActionParams<ParamsRecordType>
    ) => Promise<ActionResult<RecordType>>;
    stop: <
        ParamsRecordType extends RaRecord = any,
        RecordType extends ActionRecord = any
    >(
        resource: ResourceType,
        params: ActionParams<ParamsRecordType>
    ) => Promise<ActionResult<RecordType>>;
    getLog: <RecordType extends LogRecord = any>(
        resource: ResourceType,
        params: LogParams
    ) => Promise<LogResult<RecordType>>;
    taskStart: <
        ParamsRecordType extends RaRecord = any,
        RecordType extends ActionRecord = any
    >(
        resource: ResourceType,
        params: ActionParams<ParamsRecordType>
    ) => Promise<ActionResult<RecordType>>;
    taskStop: <
        ParamsRecordType extends RaRecord = any,
        RecordType extends ActionRecord = any
    >(
        resource: ResourceType,
        params: ActionParams<ParamsRecordType>
    ) => Promise<ActionResult<RecordType>>;
    taskTerminate: <
        ParamsRecordType extends RaRecord = any,
        RecordType extends ActionRecord = any
    >(
        resource: ResourceType,
        params: ActionParams<ParamsRecordType>
    ) => Promise<ActionResult<RecordType>>;
}
