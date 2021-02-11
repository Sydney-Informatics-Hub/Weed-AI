import React, {Component} from 'react';
import UploadDialog from '../upload/upload_dialog';
import AuthPrompt from '../auth/auth_prompt';
import { withStyles } from '@material-ui/core/styles';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import axios from 'axios';
import Button from '@material-ui/core/Button';


const useStyles = (theme) => ({
    upload_container: {
        margin: theme.spacing(10)
    },
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
            <div className={classes.upload_container}>
                { this.state.isLoggedIn
                ?
                <div>
                    <h2>Current upload status: {this.state.upload_status}</h2>
                    <p style={{color: "#f0983a"}}>{this.state.upload_status_details}</p>
                    <Button variant="outlined" color="primary" onClick={this.handleLogout}>
                        Log out
                    </Button>
                </div>
                :
                <AuthPrompt handleLogin={this.handleLogin} handleLogout={this.handleLogout}/> }
                <br />
                <p>We welcome new contributions of datasets of images with weeds already annotated.</p>
                <p>See <em>our guide</em> for collecting and annotating images.</p>
                <p>We natively support WeedCOCO format which extends on MS COCO to specify a weed ID-oriented category naming scheme, to include agricultural context and <a href="https://schema.org/Dataset" title="The Dataset schema at schema.org">schema.org/Dataset</a>-compatible metadata. We provide an uploader for MS COCO format, with forms to enter agricultural context and metadata please ensure the category names are conformant before uploading.</p>
                <p>We require that contributors license their images and annotations under the liberal <a href="https://creativecommons.org/licenses/by/4.0/" title="Creative Commons Attribution Required 4.0">CC-BY 4.0 licence</a>. Uploaders must have the rights to the content that they upload.</p>
                <br />
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <FormControl className={classes.formControl}>
                        <Select
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
            </div>
        )
    }
}

export default withStyles(useStyles)(UploadComponent);
