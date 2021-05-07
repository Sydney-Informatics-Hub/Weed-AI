import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import ErrorDialog from './dialog';

const styles = (theme) => ({
    error: {
        display: 'flex',
        float: 'right'
    },
    brief: {
        color: 'red',
        marginTop: '0.5em',
        marginRight: '1em'
    },
});

const ErrorMessage = withStyles(styles)((props) => {
    const {classes, error, details} = props;
    return (
        <div className={classes.error}>
            {error.length > 0 && error !== 'init' ? <Typography className={classes.brief}>{error}</Typography> : ""}
            {details !== "" ? <ErrorDialog error={error} details={details}/> : ""}
        </div>
    );
});

export default ErrorMessage;