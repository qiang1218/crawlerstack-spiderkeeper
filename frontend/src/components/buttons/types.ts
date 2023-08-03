import { RaRecord, RedirectionSideEffect } from "ra-core";
import { ButtonProps } from "react-admin";
import { ReactElement, ReactEventHandler } from "react";
import { UseMutationOptions } from "react-query";
import { ActionParams } from "../../jsonDataProvider";

export interface ActionButtonProps<
    RecordType extends RaRecord = any,
    MutationOptionsError = unknown
> extends ButtonProps {
    icon?: ReactElement;
    onClick?: ReactEventHandler<any>;
    mutationOptions?: UseMutationOptions<
        RecordType,
        MutationOptionsError,
        ActionParams<RecordType>
    >;
    record?: RecordType;
    redirect?: RedirectionSideEffect;
    resource?: string;
}
