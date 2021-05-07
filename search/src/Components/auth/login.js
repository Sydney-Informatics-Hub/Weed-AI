import React from 'react';
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import TextField from '@material-ui/core/TextField'
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import axios from 'axios';
import Cookies from 'js-cookie';
import AuthError from './auth_error';


const useStyles = (theme) => ({
    paper: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
    },
    form: {
        width: '100%',
        marginTop: theme.spacing(1),
    },
    submit: {
        margin: theme.spacing(3, 0, 2),
        marginTop: 0
    },
    field: {
        marginBottom: theme.spacing(2),
    },
});

const baseURL = new URL(window.location.origin);

class LoginComponent extends React.Component {

    constructor() {
        super();
        this.state = {
            error: null
        }
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleSubmit(event) {
        event.preventDefault();
        const bodyFormData = new FormData();
        const data = new FormData(event.target);
        for (const [key, value] of data.entries()) {
            bodyFormData.append(key, value);
        }
        axios({
            method: 'post',
            url: baseURL + 'api/login/',
            mode: 'same-origin',
            data: bodyFormData,
            headers: {'Content-Type': 'multipart/form-data', 'X-CSRFToken': Cookies.get('csrftoken') }
        })
        .then((response) => {
            console.log(response);
            this.props.handleLogin();
            this.props.handleClose();
        })
        .catch((error) => {
            this.setState({error: error.response.data})
        });
    }

    render() {
        const { classes } = this.props;
        return (
            <Container component="main" maxWidth="xs">
                <CssBaseline />
                <div className={classes.paper}>
                    <Typography component="h1" variant="h5">
                        Sign in
                    </Typography>
                    <form id="sign_in_submit" className={classes.form} noValidate onSubmit={this.handleSubmit} onChange={() => {this.setState({error: null})}}>
                        <TextField
                            id="username"
                            variant="outlined"
                            margin="normal"
                            required
                            fullWidth
                            label="Username"
                            name="username"
                            autoComplete="username"
                            autoFocus
                        />
                        <TextField
                            id="password"
                            variant="outlined"
                            margin="normal"
                            required
                            fullWidth
                            name="password"
                            label="Password"
                            type="password"
                            autoComplete="current-password"
                            className={classes.field}
                        />
                        <AuthError error={this.state.error} />
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            color="primary"
                            className={classes.submit}
                        >
                            Sign In
                        </Button>
                    </form>
                </div>
            </Container>
        );
    }
}

export default withStyles(useStyles)(LoginComponent);
