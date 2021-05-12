import React from "react";
import Select, { components } from "react-select";

interface Props {
    options: { value: string; label: string }[];
    value: { value: string; label: string }[];
    setValue: (value: { value: string; label: string }[]) => void;
}

const ValueContainer = (props: any) => {
    let count = props.getValue().length;
    let options_count = props.options.length;

    return (
        <components.ValueContainer {...props}>
            <span>{count === 0 ? "Nothing selected" : count <= options_count ? `${count} selected` : "Everything selected"}</span>
        </components.ValueContainer>
    );
};

export const CustomMultiSelect = (props: Props) => {
    return (
        <Select
            components={{ ValueContainer }}
            value={props.value}
            onChange={(e: any) => props.setValue(e)}
            defaultValue={props.options}
            isMulti
            name="colors"
            options={props.options}
            className="basic-multi-select"
            classNamePrefix="select"
            hideSelectedOptions={false}
            closeMenuOnSelect={false}
        />
    );
};
