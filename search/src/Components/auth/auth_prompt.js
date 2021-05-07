import React from 'react';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import LoginComponent from '../auth/login';
import RegisterComponent from '../auth/register';
import GoogleLogin from 'react-google-login';
import axios from 'axios';
import Cookies from 'js-cookie';


export default function AuthPrompt(props) {
  const baseURL = new URL(window.location.origin);
  const [open, setOpen] = React.useState(false);
  const [prompt, setPrompt] = React.useState('login');

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleLogin = () => {
    setPrompt('login');
    handleClickOpen();
  };

  const handleRegister = () => {
    setPrompt('register');
    handleClickOpen();
  };

  const responseGoogle = response => {
    console.log(response.profileObj)
    axios({
        method: 'post',
        url: baseURL + 'api/login_google/',
        mode: 'same-origin',
        data: {'email': response.profileObj.email, 'googleId': response.profileObj.googleId},
        headers: {'X-CSRFToken': Cookies.get('csrftoken') }
    })
    .then(() => props.handleLogin())
    .catch(error => {console.log(error)})
  }

  return (
    <div>
      <div style={{display: 'flex', flexDirection: 'row', alignItems: 'center'}}>
        Please&nbsp;
        <Button id="sign_in_button" variant="outlined" color="primary" onClick={handleLogin}>
            Sign In
        </Button>
        &nbsp;or&nbsp;
        <Button id="sign_up_button" variant="outlined" color="primary" onClick={handleRegister}>
            Sign up
        </Button>
        &nbsp;or&nbsp;
        <GoogleLogin
          clientId="498415135978-367uphr3ccm5upas8o5lre1h8nsthf1d.apps.googleusercontent.com"
          buttonText="Sign In with Google"
          onSuccess={responseGoogle}
          cookiePolicy={'single_host_origin'}
        />
      </div>
      <Dialog open={open} onClose={handleClose}>
        <DialogContent>
          {prompt === 'register' ? <RegisterComponent handleClose={handleClose}/> : <LoginComponent handleLogin={props.handleLogin} handleClose={handleClose}/>}
        </DialogContent>
      </Dialog>
    </div>
  );
}
