import * as React from 'react';
import { Component } from 'react';
import { Spinner } from 'reactstrap';

interface Props {
    message?: string;
}

export const CustomSpinner = (props: Props) => {


    return (<div className="fullscreen-dim">
        <div className="custom-spinner">
            <Spinner style={{ width: '5rem', height: '5rem' }}/>
            <h1>{props.message}</h1>
        </div>
    </div>)
}