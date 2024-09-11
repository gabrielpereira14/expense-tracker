const video = document.querySelector('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const expenseList = document.querySelector('#expense-list')
const scannerModal = document.querySelector('#scanner-modal')
var scanning = false; 


const videoConstraints = {
    video: {
        width: {
            min: 400,
            ideal: 720,
            max: 1080,
        },
        height: {
            min: 400,
            ideal: 720,
            max: 1080
        },
        facingMode: 'user'
    }
}
const getCameraSelection = async () => {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(device => device.kind === 'videoinput');

    if (videoDevices.length > 0){
        const selectedDevice = videoDevices[0];
        if ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices) {
            videoConstraints.deviceId = {
                    exact: selectedDevice.deviceId
                }
        }
        
    }
}

const startVideoStream = async (constraints) => {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = stream;
    video.play()

    console.debug("Stream Started")
};

const stopVideoStream = async () => {
    const stream = video.srcObject
    stream.getTracks().forEach((track) => {
        if (track.readyState == 'live' && track.kind === 'video') {
            track.stop();
        }
    });
};


const captureFrame = () => {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL('image/png');

    return dataURL;
}


getCameraSelection();  

const startScanning = async () => {
    if(!scanning){
        scanning = true;
        await startVideoStream(videoConstraints)
        openScannerModal(); 
        setTimeout(scanQrcode, 500);  
    }
}

const stopScanning = () => {
    if(scanning){
        scanning = false;
        clearCanvas();
        closeScannerModal();
        stopVideoStream()
    }
}

const openScannerModal = () => {
     scannerModal.style.display = 'flex'     
     console.debug("Modal opened")
}

const closeScannerModal = () => {
    scannerModal.style.display = 'none'
    video.pause()
}

const scanQrcode = () => {
    const image =  captureFrame();
    validateQrcode(image)
}

const validateQrcode = (image) => {
    
    var formdata = new FormData();

    formdata.append('image', image);

    requestOptions = {
        method: 'POST',
        body: formdata,
        redirect: 'follow',
        headers: {
            'X-CSRFToken' : getCookie('csrftoken')
        }
    }
    submitExpense(requestOptions)
} 

const addExpense = (expenseInfo) => {
    const expense = document.createElement("div");
    expense.classList.add("expense");

    const expenseHeader = document.createElement("div");
    expenseHeader.classList.add("expense-header");
    expenseHeader.onclick = () => toggleProductTable(expenseHeader)

    const establishmentCell = document.createElement("span");
    establishmentCell.innerHTML = expenseInfo.establishment;

    const dateCell = document.createElement("span");
    dateCell.innerHTML = expenseInfo.date;

    const totalPriceCell = document.createElement("span");
    totalPriceCell.innerHTML = `R$ ${expenseInfo.totalCost.toLocaleString()}`;

    const productsTable = document.createElement("table");
    productsTable.classList.add("products-table")

    expenseInfo.products.forEach( (product) => {
        const row = productsTable.insertRow();
        
        const nameCell = row.insertCell();
        nameCell.innerHTML = product.name;

        const quantityCell = row.insertCell();
        quantityCell.innerHTML = `${product.quantity} ${product.unit} `;

        const unitPriceCell = row.insertCell();
        unitPriceCell.innerHTML = `R$ ${product.unitPrice.toLocaleString()}`;
        
        const totalPriceCell = row.insertCell();
        totalPriceCell.innerHTML = `R$ ${product.totalPrice.toLocaleString()}`;
    })

    expenseHeader.appendChild(establishmentCell);
    expenseHeader.appendChild(dateCell);
    expenseHeader.appendChild(totalPriceCell);

    expense.appendChild(expenseHeader);
    expense.appendChild(productsTable);

    expenseList.appendChild(expense);
}


const clearCanvas = () =>{
    context.clearRect(0, 0, canvas.width, canvas.height);
}

const getCookie = (name) => {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}


const submitExpense = (requestOptions) => {
    const qrcodeValidationEndpoint = `/submit-qrcode/`;
    fetch(qrcodeValidationEndpoint, requestOptions)
    .then(response => response.json())
    .then(response => {
        if (response.ok) {
            stopScanning();
            if(response.created){
                expense = JSON.parse(response.data)
                addExpense(expense)  
            }
        }else{
            console.log(response)
            if (response.status == 409){
                //TODO
            }else{
                console.error(`Missing key in response: ${response}`)
            }
        }

    })    
    .catch(error => console.error(`Error: ${error}`))                                 
    .finally( () => {
        if(scanning) setTimeout(scanQrcode, 500);
    })
}

const toggleProductTable = (expenseHeader) => {
    const expense = expenseHeader.parentElement;

    if (!expense){
        console.log('No expense div found');
        return;
    }

    const table = expense.querySelector('.products-table');

    if (!table){
        console.log('No expense div found');
        return;
    }
    if(table.style.display == "none"){
        table.style.display = "block";
    }else{
        table.style.display = 'none';
    }
}