while getopts "u:" OPTION; do
  case "${OPTION}" in
    u)
      user="$OTPARG"
      ;;
    ?)
      echo "invalid option"
      exit 1
      ;;
  esac
done

echo "user $user"
