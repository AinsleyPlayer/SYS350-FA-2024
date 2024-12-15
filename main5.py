from time import sleep
from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim
import ssl
import getpass
import re
import vconnect

def menu():
    print(" 1: VCenter Info")
    print(" 2: Perform VM Actions")
    print(" 3: VM Details")
    print(" 0: Exit the program.")
    
def vmmenu():
    print(" 1: Power on VM")
    print(" 2: Power off VM")
    print(" 3: Take Snapshot")
    print(" 4: Delete VM")
    print(" 5: Revert To Snapshot")
    print(" 6: Rename a VM")
    print(" 0: Exit the VM Actions. ")


def connect_vcenter():
    s = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    s.check_hostname = False
    s.verify_mode = ssl.CERT_NONE 
    passw = getpass.getpass() 
    si = SmartConnect(host="vcenter01-ainsley.ainsley.local", user="administrator@vsphere.local", pwd=passw, sslContext=s) 
    return si

def get_vm_name(si, vm_name): 
    content = si.RetrieveContent() 
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True) 
    for vm in container.view: 
        if vm.name == vm_name: 
            return vm 
    return None

def power_on(vm):
    if vm.runtime.powerState != vim.VirtualMachine.PowerState.poweredOn:
        dotask = vm.PoweredOnVM_Task()
        dotask.WaitForTask()
        print("The VM Has Been Turned On. ")
    else:
        print("The VM Is Already On. ")

  
def power_off(vm):
    if vm.runtime.powerState != vim.VirtualMachine.PowerState.poweredOff:
        dotask = vm.PoweredOffVM_Task()
        dotask.WaitForTask()
        print("The VM Has Been Turned Off. ")
    else:
        print("The VM Is Already Off. ")  

def snapshot(vm, name="Snapshot", description="Milestone 5 Script Took This Snaphot. "):
    dotask = vm.CreateSnapshot_Task(name=name, description=description, memory=False, quiesce=False)
    dotask.WaitForTask()
    print("Snapshot Successfully Created. ")


def delete_vm(vm):
    dotask = vm.Destroy_Task()
    dotask.WaitForTask()
    print("VM Deleted")

def revert_to_last_snapshot(vm):
    if vm.snapshot is not None:
        snapshots = vm.snapshot.currentSnapshot
        task = snapshots.RevertToSnapshot_Task()
        task.WaitForTask()
        print("Reverted To Snapshot. ")
    else:
        print("No Snapshot Found.")
    


def rename_vm(vm, new_vm_name):
    dotask = vm.Rename_Task(new_vm_name)
    dotask.WaitForTask()
    print("VM Has Been Renamed. ")

def vm_details(vm):
    summary = vm.summary
    config = summary.config
    runtime = summary.runtime
    guest = summary.guest


    vm_deets = {
        'VM Name': config.name,
        'State': runtime.powerState,
        'CPUs': config.numCpu,
        'Memory GB': config.memorySizeMB / 1024,
        'IP Address': guest.ipAddress if guest.toolsStatus == 'toolsOK' and guest.ipAddress else 'Not Available'
    }
    return vm_deets


def main():
    si = connect_vcenter()
    menu()
    option = int(input(" Enter the option you would like to select:  "))

    while option != 0:
        if option == 1:
            print("Vcenter Info Option Selected.")
            aboutInfo=si.content.about
            print(aboutInfo)
            
            
        elif option == 2:
            print("Perform VM Actions Option Selected")
            vmmenu()
            pickchoose = int(input(" Which VM Action Would You Like To Perform?:  "))

            while pickchoose !=0:
                vm_name = input("Which VM Would You Like To Select For The Task?: ")
                vm = get_vm_name(si, vm_name)
                if not vm:
                    print("Could Not Find VM. ")
                elif pickchoose == 1:
                    power_on(vm)
                elif pickchoose == 2:
                    power_off(vm)
                elif pickchoose == 3:
                    snapshot(vm)
                elif pickchoose == 4:
                    delete_vm(vm)
                elif pickchoose == 5:
                    revert_to_last_snapshot(vm)
                elif pickchoose == 6:
                    new_vm_name = input("Enter A New Name For The VM:  ")
                    rename_vm(vm, new_vm_name)

                else:
                    print("Invalid Selection Choice." )
                    
            vmmenu()
            pickchoose = int(input(" Which VM Action Would You Like To Perform?:  "))
        
        elif option == 3:
            print("VM Details Option Selected.")
            vm_name = input("Enter The VM Name To View The Details: ")
            vm = get_vm_name(si, vm_name)
            
            if vm:
                print(vm_details(vm))
            else:
                print("No VM Found. ")

        else:
            print("Invalid Option Selected.")
            print("")
            
        menu()
        option = int(input(" Enter the option you would like to select:" ))
            
    Disconnect(si)
    print("Disconnecting now. Goodbye.")

if __name__ == "__main__": 
    main()
