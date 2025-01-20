// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

package frc.robot.commands;

import edu.wpi.first.math.geometry.Translation2d;
import edu.wpi.first.wpilibj.Timer;
import edu.wpi.first.wpilibj.smartdashboard.SmartDashboard;
import edu.wpi.first.wpilibj2.command.CommandBase;
import frc.robot.Constants;
import frc.robot.subsystems.Drivetrain;
import frc.robot.subsystems.Elbow;

public class Engage extends CommandBase {
  Drivetrain swerve;
  Elbow elbow;
  boolean isEngaged;
  double scalar = 0.05;


  /** Creates a new Engage. */
  public Engage(Drivetrain swerve, Elbow elbow) {
    // Use addRequirements() here to declare subsystem dependencies.
    this.swerve = swerve;
    this.elbow = elbow;
    addRequirements(swerve);
  }

  // Called when the command is initially scheduled.
  @Override
  public void initialize() {
    SmartDashboard.putBoolean("ENGAGE COMPLETE", false);
  }

  // Called every time the scheduler runs while the command is scheduled.
  @Override
  public void execute() {
    /* Drive */

    /* ROLL Values:
     * balanced = -0.53
     * -15.47
     * 11.47
     */

    swerve.drive(
      new Translation2d(swerve.getRoll() * scalar, 0).times(Constants.Swerve.maxSpeed), 
      0 * Constants.Swerve.maxAngularVelocity, 
      true, 
      false
    );
    }

  // Called once the command ends or is interrupted.
  @Override
  public void end(boolean interrupted) {
    swerve.stop();
    elbow.stop();
  }

  // Returns true when the command should end.
  @Override
  public boolean isFinished() {
    SmartDashboard.putBoolean("ENGAGE COMPLETE", true);
    return swerve.isEngaged(0, 0.1);
  }
}
