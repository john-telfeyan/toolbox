while getopts "u:" arg; do
  case $arg in
    ?)
      user=$OPTARG
      ;;
    ?)
      echo "Invalid option."
      ;;
  esac
done

useradd $user -m
mkdir /home/$user/.ssh
touch /home/$user/.ssh/authorized_keys
chown -R  $user:$user /home/$user/.ssh
chmod 700 /home/$user/.ssh
chmod 600 /home/$user/.ssh/authorized_keys
