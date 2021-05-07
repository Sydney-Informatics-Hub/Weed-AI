import React, {Component} from 'react';
import UploadDialog from '../upload/upload_dialog';
import AuthPrompt from '../auth/auth_prompt';
import { withStyles } from '@material-ui/core/styles';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import axios from 'axios';
import Button from '@material-ui/core/Button';
import ReactMarkdown from "react-markdown";
import content from './upload.md'
import { Helmet } from "react-helmet";
import { useArticleStyles } from '../../styles/common'


const useStyles = (theme) => ({
	...useArticleStyles(theme),
    formControl: {
        margin: theme.spacing(2),
        minWidth: 200,
    },
})

const baseURL = new URL(window.location.origin);
const upload_status_mapping = {
    'N': 'None',
    'P': 'Processing',
    'I': 'Incomplete',
    'AR': 'Awaiting Review',
    'F': 'Failed',
    'C': 'Complete'
}

class UploadComponent extends Component {
    constructor(){
        super()
        this.state = {
            isLoggedIn: false,
            upload_status: "None",
            upload_status_details: "",
            upload_type: "",
        }
        this.handleChange = this.handleChange.bind(this);
        this.retrieveUploadStatus = this.retrieveUploadStatus.bind(this);
        this.handleLogin = this.handleLogin.bind(this);
        this.handleLogout = this.handleLogout.bind(this);
    }

    handleChange(event){
        this.setState({upload_type: event.target.value})
    };

    handleLogin(){
        this.setState({isLoggedIn: true})
        this.retrieveUploadStatus()
        this.intervalID = setInterval(this.retrieveUploadStatus, 5000)
        window.location.reload(false)
    }

    handleLogout(){
        axios.get(baseURL + "api/logout/")
        .then(res => {
            console.log(res)
            this.setState({isLoggedIn: false})
            clearInterval(this.intervalID)
        })
    }

    retrieveUploadStatus(){
        axios.get(baseURL + "api/upload_status/")
        .then(res => res.data)
        .then(json => {
            this.setState({upload_status: upload_status_mapping[json.upload_status],
                           upload_status_details: json.upload_status_details})
        })
        .catch(() => {
            this.setState({upload_status: "None",
                upload_status_details: ""})
        })
    }

    retrieveLoginStatus(){
        return new Promise((resolve, reject) => {
            axios.get(baseURL + "api/login_status/")
            .then(res => {
                if(res.status === 200){
                    this.setState({isLoggedIn: true})
                    resolve(true)
                }
            })
            .catch(err => {
                reject(false)
            })
        })
    }

    componentWillMount() {
      fetch(content).then((response) => response.text()).then((text) => {
        this.setState({ markdownContent: text })
      })
    }

    async componentDidMount(){
        const isLoggedIn = await this.retrieveLoginStatus()
        if(isLoggedIn){
            this.retrieveUploadStatus()
            setInterval(this.retrieveUploadStatus, 5000)
        }
    }

    render() {
        const {classes} = this.props;
        return (
            <article className={classes.page}>
                <Helmet>
                    <title>Upload a dataset of weed imagery in crops - Weed-AI</title>
                    <meta name="description" content="Upload datasets of crop images annotated with weeds." />
                </Helmet>
                <h1>Sign In and Upload</h1>
                <p>We welcome new contributions of datasets of images with weeds already annotated.</p>
                { this.state.isLoggedIn
                ?
                <React.Fragment>
                <div>
                    <h2>Current upload status: {this.state.upload_status}</h2>
                    <p style={{color: "#f0983a"}}>{this.state.upload_status_details}</p>
                    <Button id="sign_out_button" variant="outlined" color="primary" onClick={this.handleLogout}>
                        Log out
                    </Button>
                </div>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <FormControl className={classes.formControl}>
                        <Select
                        id="annotation_format"
                        value={this.state.upload_type}
                        displayEmpty
                        onChange={this.handleChange}
                        >
                            <MenuItem value="" disabled>
                                Select annotation format
                            </MenuItem>
                            <MenuItem value="weedcoco">WeedCOCO</MenuItem>
                            <MenuItem value="coco">COCO</MenuItem>
                            <MenuItem value="voc" disabled>VOC (not implemented)</MenuItem>
                            <MenuItem value="masks" disabled>Segmentation masks (not implemented)</MenuItem>
                        </Select>
                    </FormControl>
                    <UploadDialog handleUploadStatus={this.retrieveUploadStatus} upload_type={this.state.upload_type}/>
                </div>
                </React.Fragment>
                :
                <AuthPrompt handleLogin={this.handleLogin} handleLogout={this.handleLogout}/> }

                <ReactMarkdown source={this.state.markdownContent} />
            </article>
        )
    }
}

export default withStyles(useStyles)(UploadComponent);
